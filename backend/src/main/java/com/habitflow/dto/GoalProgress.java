package com.habitflow.dto;

import com.habitflow.entity.Goal;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class GoalProgress {
    private Goal goal;
    private long completedCount;
    private long expectedCount;
    private double completionRate;
    private int currentStreakDays;
}
