package com.habitflow.service;

import com.habitflow.dto.DashboardStats;

public interface StatsService {
    DashboardStats dashboard(Long userId);
}
