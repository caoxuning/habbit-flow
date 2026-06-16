package com.habitflow.controller;

import com.habitflow.common.ApiResponse;
import com.habitflow.common.UserContext;
import com.habitflow.dto.*;
import com.habitflow.service.SocialService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/social")
@RequiredArgsConstructor
public class SocialController {
    private final SocialService socialService;

    @GetMapping("/users/search")
    public ApiResponse<List<UserSummary>> searchUsers(@RequestParam(required = false) String keyword) {
        return ApiResponse.ok(socialService.searchUsers(UserContext.getUserId(), keyword));
    }

    @GetMapping("/friends")
    public ApiResponse<List<FriendView>> friends() {
        return ApiResponse.ok(socialService.friends(UserContext.getUserId()));
    }

    @GetMapping("/friend-requests")
    public ApiResponse<List<FriendshipView>> incomingRequests() {
        return ApiResponse.ok(socialService.incomingRequests(UserContext.getUserId()));
    }

    @PostMapping("/friend-requests")
    public ApiResponse<FriendshipView> requestFriend(@Valid @RequestBody FriendRequest request) {
        return ApiResponse.ok(socialService.requestFriend(UserContext.getUserId(), request));
    }

    @PutMapping("/friend-requests/{requestId}/accept")
    public ApiResponse<FriendshipView> acceptRequest(@PathVariable Long requestId) {
        return ApiResponse.ok(socialService.acceptRequest(UserContext.getUserId(), requestId));
    }

    @PutMapping("/friend-requests/{requestId}/reject")
    public ApiResponse<FriendshipView> rejectRequest(@PathVariable Long requestId) {
        return ApiResponse.ok(socialService.rejectRequest(UserContext.getUserId(), requestId));
    }

    @GetMapping("/circles")
    public ApiResponse<List<CircleView>> circles() {
        return ApiResponse.ok(socialService.circles(UserContext.getUserId()));
    }

    @PostMapping("/circles")
    public ApiResponse<CircleView> createCircle(@Valid @RequestBody CircleRequest request) {
        return ApiResponse.ok(socialService.createCircle(UserContext.getUserId(), request));
    }

    @PostMapping("/circles/{circleId}/join")
    public ApiResponse<CircleView> joinCircle(@PathVariable Long circleId) {
        return ApiResponse.ok(socialService.joinCircle(UserContext.getUserId(), circleId));
    }

    @DeleteMapping("/circles/{circleId}/leave")
    public ApiResponse<Void> leaveCircle(@PathVariable Long circleId) {
        socialService.leaveCircle(UserContext.getUserId(), circleId);
        return ApiResponse.ok();
    }

    @GetMapping("/circles/{circleId}/posts")
    public ApiResponse<List<CirclePostView>> posts(@PathVariable Long circleId) {
        return ApiResponse.ok(socialService.posts(UserContext.getUserId(), circleId));
    }

    @PostMapping("/circles/{circleId}/posts")
    public ApiResponse<CirclePostView> publishPost(@PathVariable Long circleId,
                                                   @Valid @RequestBody CirclePostRequest request) {
        return ApiResponse.ok(socialService.publishPost(UserContext.getUserId(), circleId, request));
    }

    @GetMapping("/feed")
    public ApiResponse<List<CirclePostView>> feed() {
        return ApiResponse.ok(socialService.feed(UserContext.getUserId()));
    }
}
