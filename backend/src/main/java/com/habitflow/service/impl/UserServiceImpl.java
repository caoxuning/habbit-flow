package com.habitflow.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.habitflow.common.BusinessException;
import com.habitflow.dto.*;
import com.habitflow.entity.User;
import com.habitflow.mapper.UserMapper;
import com.habitflow.security.JwtUtil;
import com.habitflow.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Override
    @Transactional
    public AuthResponse register(AuthRequest request) {
        boolean exists = userMapper.exists(new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (exists) {
            throw new BusinessException("用户名已存在");
        }
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setCreateTime(LocalDateTime.now());
        userMapper.insert(user);
        return authResponse(user);
    }

    @Override
    public AuthResponse login(AuthRequest request) {
        User user = userMapper.selectOne(new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }
        return authResponse(user);
    }

    @Override
    public UserProfile profile(Long userId) {
        return toProfile(requireUser(userId));
    }

    @Override
    @Transactional
    public UserProfile updateProfile(Long userId, ProfileRequest request) {
        User user = requireUser(userId);
        User sameName = userMapper.selectOne(new LambdaQueryWrapper<User>()
                .eq(User::getUsername, request.getUsername())
                .ne(User::getId, userId));
        if (sameName != null) {
            throw new BusinessException("用户名已被使用");
        }
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        userMapper.updateById(user);
        return toProfile(user);
    }

    @Override
    @Transactional
    public void changePassword(Long userId, PasswordRequest request) {
        User user = requireUser(userId);
        if (!passwordEncoder.matches(request.getOldPassword(), user.getPassword())) {
            throw new BusinessException("原密码不正确");
        }
        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        userMapper.updateById(user);
    }

    private User requireUser(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }
        return user;
    }

    private AuthResponse authResponse(User user) {
        return new AuthResponse(jwtUtil.generate(user.getId(), user.getUsername()), toProfile(user));
    }

    private UserProfile toProfile(User user) {
        return new UserProfile(user.getId(), user.getUsername(), user.getEmail(), user.getCreateTime());
    }
}
