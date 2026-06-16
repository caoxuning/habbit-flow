package com.habitflow.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class FriendRequest {
    @NotNull(message = "好友用户不能为空")
    private Long targetUserId;

    private String message;
}
