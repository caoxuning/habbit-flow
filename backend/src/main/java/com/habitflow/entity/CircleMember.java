package com.habitflow.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("circle_member")
public class CircleMember {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long circleId;
    private Long userId;
    private String role;
    private LocalDateTime joinTime;
}
