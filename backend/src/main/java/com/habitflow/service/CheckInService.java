package com.habitflow.service;

import com.habitflow.dto.CheckInRequest;
import com.habitflow.entity.CheckIn;

import java.util.List;

public interface CheckInService {
    CheckIn checkIn(Long userId, CheckInRequest request);

    CheckIn makeup(Long userId, CheckInRequest request);

    List<CheckIn> list(Long userId, Long goalId);

    int currentStreakDays(Long userId);

    long completedCount(Long userId, Long goalId);
}
