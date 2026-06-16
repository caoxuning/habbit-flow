package com.habitflow.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDate;

@Data
public class GoalRequest {
    @NotBlank(message = "目标名称不能为空")
    private String name;

    @NotBlank(message = "目标类型不能为空")
    private String type;

    @NotNull(message = "开始日期不能为空")
    private LocalDate startDate;

    @NotNull(message = "结束日期不能为空")
    private LocalDate endDate;

    @NotBlank(message = "目标周期不能为空")
    private String cycle;

    @NotNull(message = "每日目标次数不能为空")
    @Min(value = 1, message = "每日目标次数至少为1")
    private Integer dailyTargetCount;

    private String status;
}
