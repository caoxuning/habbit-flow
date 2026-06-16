package com.habitflow.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("check_in")
public class CheckIn {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long goalId;
    private Long userId;
    private LocalDate checkDate;
    private LocalDateTime checkTime;
    private String status;
    private String remark;
    private Boolean makeup;
}
