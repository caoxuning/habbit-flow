package com.habitflow.controller;

import com.habitflow.common.ApiResponse;
import com.habitflow.common.UserContext;
import com.habitflow.dto.PasswordRequest;
import com.habitflow.dto.ProfileRequest;
import com.habitflow.dto.UserProfile;
import com.habitflow.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/profile")
    public ApiResponse<UserProfile> profile() {
        return ApiResponse.ok(userService.profile(UserContext.getUserId()));
    }

    @PutMapping("/profile")
    public ApiResponse<UserProfile> updateProfile(@Valid @RequestBody ProfileRequest request) {
        return ApiResponse.ok(userService.updateProfile(UserContext.getUserId(), request));
    }

    @PutMapping("/password")
    public ApiResponse<Void> changePassword(@Valid @RequestBody PasswordRequest request) {
        userService.changePassword(UserContext.getUserId(), request);
        return ApiResponse.ok();
    }
}
