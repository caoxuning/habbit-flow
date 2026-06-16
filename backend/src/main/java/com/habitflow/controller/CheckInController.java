package com.habitflow.controller;

import com.habitflow.common.ApiResponse;
import com.habitflow.common.UserContext;
import com.habitflow.dto.CheckInRequest;
import com.habitflow.entity.CheckIn;
import com.habitflow.service.CheckInService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/check-ins")
@RequiredArgsConstructor
public class CheckInController {
    private final CheckInService checkInService;

    @GetMapping
    public ApiResponse<List<CheckIn>> list(@RequestParam(required = false) Long goalId) {
        return ApiResponse.ok(checkInService.list(UserContext.getUserId(), goalId));
    }

    @PostMapping
    public ApiResponse<CheckIn> checkIn(@Valid @RequestBody CheckInRequest request) {
        return ApiResponse.ok(checkInService.checkIn(UserContext.getUserId(), request));
    }

    @PostMapping("/makeup")
    public ApiResponse<CheckIn> makeup(@Valid @RequestBody CheckInRequest request) {
        return ApiResponse.ok(checkInService.makeup(UserContext.getUserId(), request));
    }
}
