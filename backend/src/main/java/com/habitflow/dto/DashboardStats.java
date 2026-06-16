package com.habitflow.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class DashboardStats {
    private long totalGoals;
    private long activeGoals;
    private long totalCheckIns;
    private int currentStreakDays;
    private double averageCompletionRate;
    private List<MonthlyReportItem> monthlyReport;
    private List<GoalProgress> goalProgress;
}
