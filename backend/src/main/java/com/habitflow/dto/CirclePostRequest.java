package com.habitflow.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CirclePostRequest {
    @NotBlank(message = "帖子内容不能为空")
    private String content;
}
