package com.habitflow.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("goal")
public class Goal {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String name;
    private String type;
    private LocalDate startDate;
    private LocalDate endDate;
    private String cycle;
    private Integer dailyTargetCount;
    private String status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
