package com.habitflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.habitflow.dto.DashboardStats;
import com.habitflow.dto.GoalProgress;
import com.habitflow.dto.MonthlyReportItem;
import com.habitflow.entity.CheckIn;
import com.habitflow.entity.Goal;
import com.habitflow.mapper.CheckInMapper;
import com.habitflow.mapper.GoalMapper;
import com.habitflow.service.CheckInService;
import com.habitflow.service.GoalService;
import com.habitflow.service.StatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class StatsServiceImpl implements StatsService {
    private final GoalMapper goalMapper;
    private final CheckInMapper checkInMapper;
    private final GoalService goalService;
    private final CheckInService checkInService;

    @Override
    public DashboardStats dashboard(Long userId) {
        long totalGoals = goalMapper.selectCount(new LambdaQueryWrapper<Goal>().eq(Goal::getUserId, userId));
        long activeGoals = goalMapper.selectCount(new LambdaQueryWrapper<Goal>()
                .eq(Goal::getUserId, userId)
                .eq(Goal::getStatus, "ACTIVE"));
        long totalCheckIns = checkInMapper.selectCount(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getStatus, "DONE"));
        List<GoalProgress> progress = goalService.list(userId);
        double averageRate = progress.isEmpty()
                ? 0
                : progress.stream().mapToDouble(GoalProgress::getCompletionRate).average().orElse(0);
        return new DashboardStats(
                totalGoals,
                activeGoals,
                totalCheckIns,
                checkInService.currentStreakDays(userId),
                Math.round(averageRate * 10.0) / 10.0,
                monthlyReport(userId),
                progress
        );
    }

    private List<MonthlyReportItem> monthlyReport(Long userId) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM");
        List<CheckIn> rows = checkInMapper.selectList(new LambdaQueryWrapper<CheckIn>()
                .eq(CheckIn::getUserId, userId)
                .eq(CheckIn::getStatus, "DONE"));
        Map<String, Long> grouped = rows.stream()
                .collect(Collectors.groupingBy(row -> row.getCheckDate().format(formatter), Collectors.counting()));
        List<MonthlyReportItem> result = new ArrayList<>();
        LocalDate start = LocalDate.now().minusMonths(5).withDayOfMonth(1);
        for (int i = 0; i < 6; i++) {
            String month = start.plusMonths(i).format(formatter);
            result.add(new MonthlyReportItem(month, grouped.getOrDefault(month, 0L)));
        }
        return result;
    }
}
