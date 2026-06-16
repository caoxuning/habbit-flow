package com.habitflow.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class CirclePostView {
    private Long id;
    private Long circleId;
    private String circleName;
    private UserSummary author;
    private String content;
    private LocalDateTime createTime;
}
