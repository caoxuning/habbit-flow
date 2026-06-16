package com.habitflow.service;

import com.habitflow.entity.Badge;

import java.util.List;

public interface BadgeService {
    void evaluateAndGrant(Long userId);

    List<Badge> myBadges(Long userId);
}
