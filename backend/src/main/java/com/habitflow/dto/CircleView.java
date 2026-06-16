package com.habitflow.dto;

import com.habitflow.entity.SocialCircle;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class CircleView {
    private SocialCircle circle;
    private Boolean joined;
}
