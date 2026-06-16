package com.habitflow.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CircleRequest {
    @NotBlank(message = "圈子名称不能为空")
    private String name;

    @NotBlank(message = "圈子简介不能为空")
    private String description;

    private String icon;
}
