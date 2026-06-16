package com.habitflow.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("social_circle")
public class SocialCircle {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private String description;
    private String icon;
    private Long ownerUserId;
    private Integer memberCount;
    private LocalDateTime createTime;
}
