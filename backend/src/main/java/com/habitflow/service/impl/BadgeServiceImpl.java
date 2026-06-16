package com.habitflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.habitflow.entity.Badge;
import com.habitflow.entity.CheckIn;
import com.habitflow.entity.UserBadge;
import com.habitflow.mapper.BadgeMapper;
import com.habitflow.mapper.CheckInMapper;
import com.habitflow.mapper.UserBadgeMapper;
import com.habitflow.service.BadgeService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class BadgeServiceImpl implements BadgeService {
    private final BadgeMapper badgeMapper;
    private final UserBadgeMapper userBadgeMapper;
    private final CheckInMapper checkInMapper;

    @Override
    @Transactional
    public void evaluateAndGrant(Long userId) {
        long total = checkInMapper.selectCount(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getStatus, "DONE"));
        int streak = currentStreakDays(userId);
        grantIf(userId, "FIRST_CHECK_IN", total >= 1);
        grantIf(userId, "STREAK_7", streak >= 7);
        grantIf(userId, "STREAK_30", streak >= 30);
        grantIf(userId, "CHECK_IN_100", total >= 100);
        grantIf(userId, "DISCIPLINE_MASTER", total >= 100 && streak >= 30);
    }

    @Override
    public List<Badge> myBadges(Long userId) {
        Set<Long> badgeIds = userBadgeMapper.selectList(new LambdaQueryWrapper<UserBadge>()
                        .eq(UserBadge::getUserId, userId))
                .stream()
                .map(UserBadge::getBadgeId)
                .collect(Collectors.toSet());
        if (badgeIds.isEmpty()) {
            return List.of();
        }
        return badgeMapper.selectBatchIds(badgeIds);
    }

    private void grantIf(Long userId, String code, boolean matched) {
        if (!matched) {
            return;
        }
        Badge badge = badgeMapper.selectOne(new LambdaQueryWrapper<Badge>().eq(Badge::getCode, code));
        if (badge == null) {
            return;
        }
        boolean exists = userBadgeMapper.exists(new LambdaQueryWrapper<UserBadge>()
                .eq(UserBadge::getUserId, userId)
                .eq(UserBadge::getBadgeId, badge.getId()));
        if (!exists) {
            UserBadge userBadge = new UserBadge();
            userBadge.setUserId(userId);
            userBadge.setBadgeId(badge.getId());
            userBadge.setObtainedTime(LocalDateTime.now());
            userBadgeMapper.insert(userBadge);
        }
    }

    private int currentStreakDays(Long userId) {
        Set<LocalDate> dates = checkInMapper.selectList(new LambdaQueryWrapper<CheckIn>()
                        .eq(CheckIn::getUserId, userId)
                        .eq(CheckIn::getStatus, "DONE"))
                .stream()
                .map(CheckIn::getCheckDate)
                .collect(Collectors.toSet());
        int streak = 0;
        for (LocalDate date = LocalDate.now(); dates.contains(date); date = date.minusDays(1)) {
            streak++;
        }
        return streak;
    }
}
