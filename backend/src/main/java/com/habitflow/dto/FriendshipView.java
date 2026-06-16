package com.habitflow.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class FriendshipView {
    private Long id;
    private UserSummary requester;
    private UserSummary addressee;
    private String status;
    private String message;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
