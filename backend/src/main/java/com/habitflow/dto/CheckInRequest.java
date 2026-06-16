package com.habitflow.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDate;

@Data
public class CheckInRequest {
    @NotNull(message = "目标编号不能为空")
    private Long goalId;
    private LocalDate checkDate;
    private String remark;
}
