package com.habitflow.controller;

import com.habitflow.common.ApiResponse;
import com.habitflow.common.UserContext;
import com.habitflow.entity.Badge;
import com.habitflow.service.BadgeService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/badges")
@RequiredArgsConstructor
public class BadgeController {
    private final BadgeService badgeService;

    @GetMapping("/mine")
    public ApiResponse<List<Badge>> mine() {
        return ApiResponse.ok(badgeService.myBadges(UserContext.getUserId()));
    }
}
