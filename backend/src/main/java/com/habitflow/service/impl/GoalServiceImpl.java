package com.habitflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.habitflow.common.BusinessException;
import com.habitflow.dto.GoalProgress;
import com.habitflow.dto.GoalRequest;
import com.habitflow.entity.CheckIn;
import com.habitflow.entity.Goal;
import com.habitflow.mapper.CheckInMapper;
import com.habitflow.mapper.GoalMapper;
import com.habitflow.service.GoalService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class GoalServiceImpl implements GoalService {
    private final GoalMapper goalMapper;
    private final CheckInMapper checkInMapper;

    @Override
    @Transactional
    public Goal create(Long userId, GoalRequest request) {
        validateDateRange(request);
        Goal goal = new Goal();
        fillGoal(goal, request);
        goal.setUserId(userId);
        goal.setStatus(request.getStatus() == null ? "ACTIVE" : request.getStatus());
        goal.setCreateTime(LocalDateTime.now());
        goal.setUpdateTime(LocalDateTime.now());
        goalMapper.insert(goal);
        return goal;
    }

    @Override
    @Transactional
    public Goal update(Long userId, Long goalId, GoalRequest request) {
        validateDateRange(request);
        Goal goal = getOwnedGoal(userId, goalId);
        fillGoal(goal, request);
        goal.setStatus(request.getStatus() == null ? goal.getStatus() : request.getStatus());
        goal.setUpdateTime(LocalDateTime.now());
        goalMapper.updateById(goal);
        return goal;
    }

    @Override
    @Transactional
    public void delete(Long userId, Long goalId) {
        Goal goal = getOwnedGoal(userId, goalId);
        goalMapper.deleteById(goal.getId());
        checkInMapper.delete(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getGoalId, goalId));
    }

    @Override
    public List<GoalProgress> list(Long userId) {
        return goalMapper.selectList(new LambdaQueryWrapper<Goal>()
                        .eq(Goal::getUserId, userId)
                        .orderByDesc(Goal::getCreateTime))
                .stream()
                .map(goal -> {
                    long completed = completedCount(userId, goal.getId());
                    long expected = expectedCount(goal, LocalDate.now());
                    double rate = expected == 0 ? 0 : Math.min(100, completed * 100.0 / expected);
                    return new GoalProgress(goal, completed, expected, Math.round(rate * 10.0) / 10.0,
                            currentStreakDays(userId));
                })
                .toList();
    }

    @Override
    public Goal getOwnedGoal(Long userId, Long goalId) {
        Goal goal = goalMapper.selectOne(new LambdaQueryWrapper<Goal>()
                .eq(Goal::getId, goalId)
                .eq(Goal::getUserId, userId));
        if (goal == null) {
            throw new BusinessException(404, "目标不存在");
        }
        return goal;
    }

    static long expectedCount(Goal goal, LocalDate today) {
        LocalDate end = goal.getEndDate().isAfter(today) ? today : goal.getEndDate();
        if (end.isBefore(goal.getStartDate())) {
            return 0;
        }
        long days = ChronoUnit.DAYS.between(goal.getStartDate(), end) + 1;
        long occurrences = switch (goal.getCycle()) {
            case "WEEKLY" -> countWeekly(goal.getStartDate(), end);
            case "MONTHLY" -> countMonthly(goal.getStartDate(), end);
            default -> days;
        };
        return occurrences * goal.getDailyTargetCount();
    }

    private static long countWeekly(LocalDate start, LocalDate end) {
        long count = 0;
        for (LocalDate date = start; !date.isAfter(end); date = date.plusDays(1)) {
            if (date.getDayOfWeek() == DayOfWeek.MONDAY) {
                count++;
            }
        }
        return Math.max(1, count);
    }

    private static long countMonthly(LocalDate start, LocalDate end) {
        return ChronoUnit.MONTHS.between(start.withDayOfMonth(1), end.withDayOfMonth(1)) + 1;
    }

    private long completedCount(Long userId, Long goalId) {
        return checkInMapper.selectCount(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getGoalId, goalId)
                .eq(CheckIn::getStatus, "DONE"));
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

    private void fillGoal(Goal goal, GoalRequest request) {
        goal.setName(request.getName());
        goal.setType(request.getType());
        goal.setStartDate(request.getStartDate());
        goal.setEndDate(request.getEndDate());
        goal.setCycle(request.getCycle());
        goal.setDailyTargetCount(request.getDailyTargetCount());
    }

    private void validateDateRange(GoalRequest request) {
        if (request.getEndDate().isBefore(request.getStartDate())) {
            throw new BusinessException("结束日期不能早于开始日期");
        }
    }
}
