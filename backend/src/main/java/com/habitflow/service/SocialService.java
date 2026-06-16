package com.habitflow.service;

import com.habitflow.dto.*;

import java.util.List;

public interface SocialService {
    List<UserSummary> searchUsers(Long userId, String keyword);

    List<FriendView> friends(Long userId);

    List<FriendshipView> incomingRequests(Long userId);

    FriendshipView requestFriend(Long userId, FriendRequest request);

    FriendshipView acceptRequest(Long userId, Long requestId);

    FriendshipView rejectRequest(Long userId, Long requestId);

    List<CircleView> circles(Long userId);

    CircleView createCircle(Long userId, CircleRequest request);

    CircleView joinCircle(Long userId, Long circleId);

    void leaveCircle(Long userId, Long circleId);

    List<CirclePostView> posts(Long userId, Long circleId);

    List<CirclePostView> feed(Long userId);

    CirclePostView publishPost(Long userId, Long circleId, CirclePostRequest request);
}
