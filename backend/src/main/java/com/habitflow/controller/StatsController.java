package com.habitflow.controller;

import com.habitflow.common.ApiResponse;
import com.habitflow.common.UserContext;
import com.habitflow.dto.DashboardStats;
import com.habitflow.service.StatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/stats")
@RequiredArgsConstructor
public class StatsController {
    private final StatsService statsService;

    @GetMapping("/dashboard")
    public ApiResponse<DashboardStats> dashboard() {
        return ApiResponse.ok(statsService.dashboard(UserContext.getUserId()));
    }
}
