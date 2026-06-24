-- ============================================================
-- HabitFlow 自律目标追踪平台 数据库建表脚本
-- 适用数据库：MySQL 8.0+
-- 字符集：utf8mb4
-- 用途：可用于 MySQL Workbench 反向工程生成 ER 图
-- ============================================================

CREATE DATABASE IF NOT EXISTS habitflow
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE habitflow;

-- -----------------------------------------------------------
-- 1. 用户表
-- -----------------------------------------------------------
CREATE TABLE user (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    email       VARCHAR(120),
    create_time DATETIME     NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 2. 目标表
-- -----------------------------------------------------------
CREATE TABLE goal (
    id                 BIGINT       PRIMARY KEY AUTO_INCREMENT,
    user_id            BIGINT       NOT NULL,
    name               VARCHAR(120) NOT NULL,
    type               VARCHAR(50)  NOT NULL,
    start_date         DATE         NOT NULL,
    end_date           DATE         NOT NULL,
    cycle              VARCHAR(20)  NOT NULL COMMENT 'DAILY / WEEKLY / MONTHLY',
    daily_target_count INT          NOT NULL DEFAULT 1,
    status             VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE / PAUSED / DONE',
    create_time        DATETIME     NOT NULL,
    update_time        DATETIME     NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 3. 打卡记录表
-- -----------------------------------------------------------
CREATE TABLE check_in (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT,
    goal_id     BIGINT       NOT NULL,
    user_id     BIGINT       NOT NULL,
    check_date  DATE         NOT NULL,
    check_time  DATETIME     NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'DONE',
    remark      VARCHAR(500),
    makeup      BOOLEAN      NOT NULL DEFAULT FALSE COMMENT '是否补卡',
    FOREIGN KEY (goal_id) REFERENCES goal(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 4. 勋章定义表
-- -----------------------------------------------------------
CREATE TABLE badge (
    id             BIGINT       PRIMARY KEY AUTO_INCREMENT,
    code           VARCHAR(50)  NOT NULL UNIQUE,
    name           VARCHAR(80)  NOT NULL,
    description    VARCHAR(255) NOT NULL,
    condition_text VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 5. 用户勋章关联表
-- -----------------------------------------------------------
CREATE TABLE user_badge (
    id             BIGINT    PRIMARY KEY AUTO_INCREMENT,
    user_id        BIGINT    NOT NULL,
    badge_id       BIGINT    NOT NULL,
    obtained_time  DATETIME  NOT NULL,
    FOREIGN KEY (user_id)  REFERENCES user(id),
    FOREIGN KEY (badge_id) REFERENCES badge(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 6. 消息提醒表
-- -----------------------------------------------------------
CREATE TABLE notification (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT,
    user_id     BIGINT       NOT NULL,
    content     VARCHAR(500) NOT NULL,
    is_read     BOOLEAN      NOT NULL DEFAULT FALSE,
    create_time DATETIME     NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 7. 好友关系表
-- -----------------------------------------------------------
CREATE TABLE friendship (
    id            BIGINT      PRIMARY KEY AUTO_INCREMENT,
    requester_id  BIGINT      NOT NULL COMMENT '申请方',
    addressee_id  BIGINT      NOT NULL COMMENT '接收方',
    status        VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING / ACCEPTED / REJECTED',
    create_time   DATETIME    NOT NULL,
    FOREIGN KEY (requester_id) REFERENCES user(id),
    FOREIGN KEY (addressee_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 8. 打卡圈子表
-- -----------------------------------------------------------
CREATE TABLE social_circle (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(80)  NOT NULL UNIQUE,
    description VARCHAR(255),
    icon        VARCHAR(100),
    owner_id    BIGINT       NOT NULL,
    create_time DATETIME     NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 9. 圈子成员表
-- -----------------------------------------------------------
CREATE TABLE circle_member (
    id         BIGINT   PRIMARY KEY AUTO_INCREMENT,
    circle_id  BIGINT   NOT NULL,
    user_id    BIGINT   NOT NULL,
    join_time  DATETIME NOT NULL,
    FOREIGN KEY (circle_id) REFERENCES social_circle(id),
    FOREIGN KEY (user_id)   REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 10. 圈子帖子表
-- -----------------------------------------------------------
CREATE TABLE circle_post (
    id          BIGINT   PRIMARY KEY AUTO_INCREMENT,
    circle_id   BIGINT   NOT NULL,
    user_id     BIGINT   NOT NULL,
    content     TEXT     NOT NULL,
    create_time DATETIME NOT NULL,
    FOREIGN KEY (circle_id) REFERENCES social_circle(id),
    FOREIGN KEY (user_id)   REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
