package com.habitflow.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class FriendView {
    private Long friendshipId;
    private UserSummary friend;
    private LocalDateTime sinceTime;
}
