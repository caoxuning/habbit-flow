package com.habitflow.controller;

import com.habitflow.common.ApiResponse;
import com.habitflow.common.UserContext;
import com.habitflow.dto.GoalProgress;
import com.habitflow.dto.GoalRequest;
import com.habitflow.entity.Goal;
import com.habitflow.service.GoalService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/goals")
@RequiredArgsConstructor
public class GoalController {
    private final GoalService goalService;

    @GetMapping
    public ApiResponse<List<GoalProgress>> list() {
        return ApiResponse.ok(goalService.list(UserContext.getUserId()));
    }

    @PostMapping
    public ApiResponse<Goal> create(@Valid @RequestBody GoalRequest request) {
        return ApiResponse.ok(goalService.create(UserContext.getUserId(), request));
    }

    @PutMapping("/{goalId}")
    public ApiResponse<Goal> update(@PathVariable Long goalId, @Valid @RequestBody GoalRequest request) {
        return ApiResponse.ok(goalService.update(UserContext.getUserId(), goalId, request));
    }

    @DeleteMapping("/{goalId}")
    public ApiResponse<Void> delete(@PathVariable Long goalId) {
        goalService.delete(UserContext.getUserId(), goalId);
        return ApiResponse.ok();
    }
}
