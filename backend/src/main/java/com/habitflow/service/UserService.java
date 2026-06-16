package com.habitflow.service;

import com.habitflow.dto.*;

public interface UserService {
    AuthResponse register(AuthRequest request);

    AuthResponse login(AuthRequest request);

    UserProfile profile(Long userId);

    UserProfile updateProfile(Long userId, ProfileRequest request);

    void changePassword(Long userId, PasswordRequest request);
}
