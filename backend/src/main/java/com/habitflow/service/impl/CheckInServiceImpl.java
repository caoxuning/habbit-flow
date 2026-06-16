package com.habitflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.habitflow.common.BusinessException;
import com.habitflow.dto.CheckInRequest;
import com.habitflow.entity.CheckIn;
import com.habitflow.entity.Goal;
import com.habitflow.mapper.CheckInMapper;
import com.habitflow.service.BadgeService;
import com.habitflow.service.CheckInService;
import com.habitflow.service.GoalService;
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
public class CheckInServiceImpl implements CheckInService {
    private final CheckInMapper checkInMapper;
    private final GoalService goalService;
    private final BadgeService badgeService;

    @Override
    @Transactional
    public CheckIn checkIn(Long userId, CheckInRequest request) {
        LocalDate date = request.getCheckDate() == null ? LocalDate.now() : request.getCheckDate();
        if (!date.equals(LocalDate.now())) {
            throw new BusinessException("每日打卡只能提交当天记录，历史日期请使用补卡");
        }
        return saveCheckIn(userId, request, date, false);
    }

    @Override
    @Transactional
    public CheckIn makeup(Long userId, CheckInRequest request) {
        LocalDate date = request.getCheckDate();
        if (date == null || !date.isBefore(LocalDate.now())) {
            throw new BusinessException("补卡日期必须早于今天");
        }
        return saveCheckIn(userId, request, date, true);
    }

    @Override
    public List<CheckIn> list(Long userId, Long goalId) {
        LambdaQueryWrapper<CheckIn> wrapper = new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .orderByDesc(CheckIn::getCheckDate)
                .orderByDesc(CheckIn::getCheckTime);
        if (goalId != null) {
            wrapper.eq(CheckIn::getGoalId, goalId);
        }
        return checkInMapper.selectList(wrapper);
    }

    @Override
    public int currentStreakDays(Long userId) {
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

    @Override
    public long completedCount(Long userId, Long goalId) {
        return checkInMapper.selectCount(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getGoalId, goalId)
                .eq(CheckIn::getStatus, "DONE"));
    }

    private CheckIn saveCheckIn(Long userId, CheckInRequest request, LocalDate date, boolean makeup) {
        Goal goal = goalService.getOwnedGoal(userId, request.getGoalId());
        if (!"ACTIVE".equals(goal.getStatus())) {
            throw new BusinessException("目标未处于进行中状态");
        }
        if (date.isBefore(goal.getStartDate()) || date.isAfter(goal.getEndDate())) {
            throw new BusinessException("打卡日期不在目标周期内");
        }
        boolean exists = checkInMapper.exists(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getGoalId, request.getGoalId())
                .eq(CheckIn::getCheckDate, date));
        if (exists) {
            throw new BusinessException("该目标当天已打卡");
        }
        CheckIn checkIn = new CheckIn();
        checkIn.setUserId(userId);
        checkIn.setGoalId(request.getGoalId());
        checkIn.setCheckDate(date);
        checkIn.setCheckTime(LocalDateTime.now());
        checkIn.setStatus("DONE");
        checkIn.setRemark(request.getRemark());
        checkIn.setMakeup(makeup);
        checkInMapper.insert(checkIn);
        badgeService.evaluateAndGrant(userId);
        return checkIn;
    }
}
