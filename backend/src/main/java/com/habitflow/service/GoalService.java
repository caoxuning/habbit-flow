package com.habitflow.service;

import com.habitflow.dto.GoalProgress;
import com.habitflow.dto.GoalRequest;
import com.habitflow.entity.Goal;

import java.util.List;

public interface GoalService {
    Goal create(Long userId, GoalRequest request);

    Goal update(Long userId, Long goalId, GoalRequest request);

    void delete(Long userId, Long goalId);

    List<GoalProgress> list(Long userId);

    Goal getOwnedGoal(Long userId, Long goalId);
}
