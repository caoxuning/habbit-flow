package com.habitflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.habitflow.common.BusinessException;
import com.habitflow.dto.*;
import com.habitflow.entity.CircleMember;
import com.habitflow.entity.CirclePost;
import com.habitflow.entity.Friendship;
import com.habitflow.entity.SocialCircle;
import com.habitflow.entity.User;
import com.habitflow.mapper.CircleMemberMapper;
import com.habitflow.mapper.CirclePostMapper;
import com.habitflow.mapper.FriendshipMapper;
import com.habitflow.mapper.SocialCircleMapper;
import com.habitflow.mapper.UserMapper;
import com.habitflow.service.SocialService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class SocialServiceImpl implements SocialService {
    private final UserMapper userMapper;
    private final FriendshipMapper friendshipMapper;
    private final SocialCircleMapper socialCircleMapper;
    private final CircleMemberMapper circleMemberMapper;
    private final CirclePostMapper circlePostMapper;

    @Override
    public List<UserSummary> searchUsers(Long userId, String keyword) {
        String trimmed = keyword == null ? "" : keyword.trim();
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
                .ne(User::getId, userId)
                .orderByAsc(User::getUsername)
                .last("LIMIT 20");
        if (!trimmed.isBlank()) {
            wrapper.like(User::getUsername, trimmed);
        }
        return userMapper.selectList(wrapper).stream().map(this::summary).toList();
    }

    @Override
    public List<FriendView> friends(Long userId) {
        return friendshipMapper.selectList(new LambdaQueryWrapper<Friendship>()
                        .eq(Friendship::getStatus, "ACCEPTED")
                        .and(w -> w.eq(Friendship::getRequesterId, userId).or().eq(Friendship::getAddresseeId, userId))
                        .orderByDesc(Friendship::getUpdateTime))
                .stream()
                .map(friendship -> {
                    Long friendId = friendship.getRequesterId().equals(userId)
                            ? friendship.getAddresseeId()
                            : friendship.getRequesterId();
                    return new FriendView(friendship.getId(), summary(userMapper.selectById(friendId)),
                            friendship.getUpdateTime());
                })
                .toList();
    }

    @Override
    public List<FriendshipView> incomingRequests(Long userId) {
        return friendshipMapper.selectList(new LambdaQueryWrapper<Friendship>()
                        .eq(Friendship::getAddresseeId, userId)
                        .eq(Friendship::getStatus, "PENDING")
                        .orderByDesc(Friendship::getCreateTime))
                .stream()
                .map(this::view)
                .toList();
    }

    @Override
    @Transactional
    public FriendshipView requestFriend(Long userId, FriendRequest request) {
        Long targetUserId = request.getTargetUserId();
        if (userId.equals(targetUserId)) {
            throw new BusinessException("不能添加自己为好友");
        }
        if (userMapper.selectById(targetUserId) == null) {
            throw new BusinessException(404, "用户不存在");
        }
        Friendship existing = findFriendshipBetween(userId, targetUserId);
        if (existing != null) {
            if ("ACCEPTED".equals(existing.getStatus())) {
                throw new BusinessException("你们已经是好友");
            }
            if ("PENDING".equals(existing.getStatus())) {
                throw new BusinessException("好友申请已存在");
            }
            existing.setRequesterId(userId);
            existing.setAddresseeId(targetUserId);
            existing.setStatus("PENDING");
            existing.setMessage(request.getMessage());
            existing.setUpdateTime(LocalDateTime.now());
            friendshipMapper.updateById(existing);
            return view(existing);
        }
        Friendship friendship = new Friendship();
        friendship.setRequesterId(userId);
        friendship.setAddresseeId(targetUserId);
        friendship.setStatus("PENDING");
        friendship.setMessage(request.getMessage());
        friendship.setCreateTime(LocalDateTime.now());
        friendship.setUpdateTime(LocalDateTime.now());
        friendshipMapper.insert(friendship);
        return view(friendship);
    }

    @Override
    @Transactional
    public FriendshipView acceptRequest(Long userId, Long requestId) {
        Friendship friendship = ownedIncomingRequest(userId, requestId);
        friendship.setStatus("ACCEPTED");
        friendship.setUpdateTime(LocalDateTime.now());
        friendshipMapper.updateById(friendship);
        return view(friendship);
    }

    @Override
    @Transactional
    public FriendshipView rejectRequest(Long userId, Long requestId) {
        Friendship friendship = ownedIncomingRequest(userId, requestId);
        friendship.setStatus("REJECTED");
        friendship.setUpdateTime(LocalDateTime.now());
        friendshipMapper.updateById(friendship);
        return view(friendship);
    }

    @Override
    public List<CircleView> circles(Long userId) {
        Set<Long> joinedIds = circleMemberMapper.selectList(new LambdaQueryWrapper<CircleMember>()
                        .eq(CircleMember::getUserId, userId))
                .stream()
                .map(CircleMember::getCircleId)
                .collect(Collectors.toSet());
        return socialCircleMapper.selectList(new LambdaQueryWrapper<SocialCircle>()
                        .orderByDesc(SocialCircle::getMemberCount)
                        .orderByAsc(SocialCircle::getName))
                .stream()
                .map(circle -> new CircleView(circle, joinedIds.contains(circle.getId())))
                .toList();
    }

    @Override
    @Transactional
    public CircleView createCircle(Long userId, CircleRequest request) {
        boolean exists = socialCircleMapper.exists(new LambdaQueryWrapper<SocialCircle>()
                .eq(SocialCircle::getName, request.getName()));
        if (exists) {
            throw new BusinessException("圈子名称已存在");
        }
        SocialCircle circle = new SocialCircle();
        circle.setName(request.getName());
        circle.setDescription(request.getDescription());
        circle.setIcon(request.getIcon() == null || request.getIcon().isBlank() ? "TAG" : request.getIcon());
        circle.setOwnerUserId(userId);
        circle.setMemberCount(1);
        circle.setCreateTime(LocalDateTime.now());
        socialCircleMapper.insert(circle);
        addMember(userId, circle.getId(), "OWNER");
        return new CircleView(circle, true);
    }

    @Override
    @Transactional
    public CircleView joinCircle(Long userId, Long circleId) {
        SocialCircle circle = requiredCircle(circleId);
        if (isMember(userId, circleId)) {
            return new CircleView(circle, true);
        }
        addMember(userId, circleId, "MEMBER");
        circle.setMemberCount(circle.getMemberCount() + 1);
        socialCircleMapper.updateById(circle);
        return new CircleView(circle, true);
    }

    @Override
    @Transactional
    public void leaveCircle(Long userId, Long circleId) {
        SocialCircle circle = requiredCircle(circleId);
        if (userId.equals(circle.getOwnerUserId())) {
            throw new BusinessException("圈主不能直接退出自己创建的圈子");
        }
        int deleted = circleMemberMapper.delete(new LambdaQueryWrapper<CircleMember>()
                .eq(CircleMember::getUserId, userId)
                .eq(CircleMember::getCircleId, circleId));
        if (deleted > 0) {
            circle.setMemberCount(Math.max(0, circle.getMemberCount() - 1));
            socialCircleMapper.updateById(circle);
        }
    }

    @Override
    public List<CirclePostView> posts(Long userId, Long circleId) {
        requiredCircle(circleId);
        return circlePostMapper.selectList(new LambdaQueryWrapper<CirclePost>()
                        .eq(CirclePost::getCircleId, circleId)
                        .orderByDesc(CirclePost::getCreateTime)
                        .last("LIMIT 50"))
                .stream()
                .map(this::postView)
                .toList();
    }

    @Override
    public List<CirclePostView> feed(Long userId) {
        List<Long> circleIds = circleMemberMapper.selectList(new LambdaQueryWrapper<CircleMember>()
                        .eq(CircleMember::getUserId, userId))
                .stream()
                .map(CircleMember::getCircleId)
                .toList();
        if (circleIds.isEmpty()) {
            return List.of();
        }
        return circlePostMapper.selectList(new LambdaQueryWrapper<CirclePost>()
                        .in(CirclePost::getCircleId, circleIds)
                        .orderByDesc(CirclePost::getCreateTime)
                        .last("LIMIT 50"))
                .stream()
                .map(this::postView)
                .toList();
    }

    @Override
    @Transactional
    public CirclePostView publishPost(Long userId, Long circleId, CirclePostRequest request) {
        requiredCircle(circleId);
        if (!isMember(userId, circleId)) {
            throw new BusinessException("加入圈子后才能发帖");
        }
        CirclePost post = new CirclePost();
        post.setCircleId(circleId);
        post.setUserId(userId);
        post.setContent(request.getContent());
        post.setCreateTime(LocalDateTime.now());
        circlePostMapper.insert(post);
        return postView(post);
    }

    private Friendship ownedIncomingRequest(Long userId, Long requestId) {
        Friendship friendship = friendshipMapper.selectById(requestId);
        if (friendship == null || !friendship.getAddresseeId().equals(userId)
                || !"PENDING".equals(friendship.getStatus())) {
            throw new BusinessException(404, "好友申请不存在");
        }
        return friendship;
    }

    private Friendship findFriendshipBetween(Long firstUserId, Long secondUserId) {
        return friendshipMapper.selectOne(new LambdaQueryWrapper<Friendship>()
                .and(w -> w.eq(Friendship::getRequesterId, firstUserId)
                        .eq(Friendship::getAddresseeId, secondUserId))
                .or(w -> w.eq(Friendship::getRequesterId, secondUserId)
                        .eq(Friendship::getAddresseeId, firstUserId))
                .last("LIMIT 1"));
    }

    private SocialCircle requiredCircle(Long circleId) {
        SocialCircle circle = socialCircleMapper.selectById(circleId);
        if (circle == null) {
            throw new BusinessException(404, "圈子不存在");
        }
        return circle;
    }

    private boolean isMember(Long userId, Long circleId) {
        return circleMemberMapper.exists(new LambdaQueryWrapper<CircleMember>()
                .eq(CircleMember::getUserId, userId)
                .eq(CircleMember::getCircleId, circleId));
    }

    private void addMember(Long userId, Long circleId, String role) {
        CircleMember member = new CircleMember();
        member.setUserId(userId);
        member.setCircleId(circleId);
        member.setRole(role);
        member.setJoinTime(LocalDateTime.now());
        circleMemberMapper.insert(member);
    }

    private FriendshipView view(Friendship friendship) {
        return new FriendshipView(
                friendship.getId(),
                summary(userMapper.selectById(friendship.getRequesterId())),
                summary(userMapper.selectById(friendship.getAddresseeId())),
                friendship.getStatus(),
                friendship.getMessage(),
                friendship.getCreateTime(),
                friendship.getUpdateTime()
        );
    }

    private CirclePostView postView(CirclePost post) {
        SocialCircle circle = socialCircleMapper.selectById(post.getCircleId());
        return new CirclePostView(
                post.getId(),
                post.getCircleId(),
                circle == null ? "未知圈子" : circle.getName(),
                summary(userMapper.selectById(post.getUserId())),
                post.getContent(),
                post.getCreateTime()
        );
    }

    private UserSummary summary(User user) {
        if (user == null) {
            return new UserSummary(null, "未知用户", null);
        }
        return new UserSummary(user.getId(), user.getUsername(), user.getEmail());
    }
}
