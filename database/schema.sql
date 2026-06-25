-- ============================================================
-- HabitFlow 自律目标追踪平台 数据库完整建表脚本
-- 适用数据库：MySQL 8.0+
-- 字符集：utf8mb4
-- 说明：基于云数据库实际结构的终版
-- ============================================================

CREATE DATABASE IF NOT EXISTS habitflow
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE habitflow;

-- -----------------------------------------------------------
-- 1. 用户表
-- -----------------------------------------------------------
CREATE TABLE user (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '用户编号',
    username    VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    password    VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    email       VARCHAR(120) DEFAULT NULL COMMENT '邮箱',
    create_time DATETIME     NOT NULL COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- -----------------------------------------------------------
-- 2. 目标表
-- -----------------------------------------------------------
CREATE TABLE goal (
    id                 BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '目标编号',
    user_id            BIGINT       NOT NULL COMMENT '用户编号',
    name               VARCHAR(120) NOT NULL COMMENT '目标名称',
    type               VARCHAR(50)  NOT NULL COMMENT '目标类型（运动/英语/阅读/学习等）',
    start_date         DATE         NOT NULL COMMENT '开始日期',
    end_date           DATE         NOT NULL COMMENT '结束日期',
    cycle              VARCHAR(20)  NOT NULL COMMENT '目标周期：DAILY/WEEKLY/MONTHLY',
    daily_target_count INT          NOT NULL DEFAULT 1 COMMENT '每日目标次数',
    priority           VARCHAR(20)  NOT NULL DEFAULT 'NORMAL' COMMENT '优先级：LOW/NORMAL/HIGH/URGENT',
    status             VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE/PAUSED/DONE',
    create_time        DATETIME     NOT NULL COMMENT '创建时间',
    update_time        DATETIME     NOT NULL COMMENT '更新时间',
    INDEX idx_goal_user (user_id),
    CONSTRAINT fk_goal_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='目标表';

-- -----------------------------------------------------------
-- 3. 打卡记录表
-- -----------------------------------------------------------
CREATE TABLE check_in (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '打卡编号',
    goal_id     BIGINT       NOT NULL COMMENT '目标编号',
    user_id     BIGINT       NOT NULL COMMENT '用户编号',
    check_date  DATE         NOT NULL COMMENT '打卡日期',
    check_time  DATETIME     NOT NULL COMMENT '打卡时间（精确到时分秒）',
    status      VARCHAR(20)  NOT NULL DEFAULT 'DONE' COMMENT '打卡状态：DONE',
    remark      VARCHAR(500) DEFAULT NULL COMMENT '备注内容',
    makeup      TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否补卡：0=正常打卡, 1=补卡',
    INDEX idx_check_goal (goal_id),
    INDEX idx_check_user (user_id),
    CONSTRAINT fk_check_goal FOREIGN KEY (goal_id) REFERENCES goal(id),
    CONSTRAINT fk_check_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='打卡记录表';

-- -----------------------------------------------------------
-- 4. 勋章定义表
-- -----------------------------------------------------------
CREATE TABLE badge (
    id             BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '勋章编号',
    code           VARCHAR(50)  NOT NULL UNIQUE COMMENT '勋章编码（用于程序判断）',
    name           VARCHAR(80)  NOT NULL COMMENT '勋章名称',
    description    VARCHAR(255) NOT NULL COMMENT '勋章描述',
    condition_text VARCHAR(255) NOT NULL COMMENT '获取条件（前台展示文字）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='勋章定义表';

-- -----------------------------------------------------------
-- 5. 用户勋章关联表
-- -----------------------------------------------------------
CREATE TABLE user_badge (
    id             BIGINT   PRIMARY KEY AUTO_INCREMENT COMMENT '记录编号',
    user_id        BIGINT   NOT NULL COMMENT '用户编号',
    badge_id       BIGINT   NOT NULL COMMENT '勋章编号',
    obtained_time  DATETIME NOT NULL COMMENT '获得时间',
    INDEX idx_ub_user (user_id),
    INDEX idx_ub_badge (badge_id),
    CONSTRAINT fk_user_badge_user FOREIGN KEY (user_id) REFERENCES user(id),
    CONSTRAINT fk_user_badge_badge FOREIGN KEY (badge_id) REFERENCES badge(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户勋章关联表';

-- -----------------------------------------------------------
-- 6. 消息通知表
-- -----------------------------------------------------------
CREATE TABLE notification (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '通知编号',
    user_id     BIGINT       NOT NULL COMMENT '接收用户编号',
    type        VARCHAR(50)  NOT NULL COMMENT '通知类型（如 BADGE/FRIEND/SYSTEM）',
    title       VARCHAR(120) NOT NULL COMMENT '通知标题',
    content     VARCHAR(500) NOT NULL COMMENT '通知内容',
    is_read     TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否已读：0=未读, 1=已读',
    create_time DATETIME     NOT NULL COMMENT '创建时间',
    INDEX idx_noti_user (user_id),
    CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息通知表';

-- -----------------------------------------------------------
-- 7. 好友关系表
-- -----------------------------------------------------------
CREATE TABLE friendship (
    id            BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '好友关系编号',
    requester_id  BIGINT       NOT NULL COMMENT '申请方用户编号',
    addressee_id  BIGINT       NOT NULL COMMENT '接收方用户编号',
    status        VARCHAR(20)  NOT NULL DEFAULT 'PENDING' COMMENT '状态：PENDING/ACCEPTED/REJECTED',
    message       VARCHAR(255) DEFAULT NULL COMMENT '申请留言',
    create_time   DATETIME     NOT NULL COMMENT '创建时间',
    update_time   DATETIME     NOT NULL COMMENT '更新时间',
    INDEX idx_friend_requester (requester_id),
    INDEX idx_friend_addressee (addressee_id),
    CONSTRAINT fk_friend_requester FOREIGN KEY (requester_id) REFERENCES user(id),
    CONSTRAINT fk_friend_addressee FOREIGN KEY (addressee_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='好友关系表';

-- -----------------------------------------------------------
-- 8. 打卡圈子表
-- -----------------------------------------------------------
CREATE TABLE social_circle (
    id             BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '圈子编号',
    name           VARCHAR(80)  NOT NULL UNIQUE COMMENT '圈子名称',
    description    VARCHAR(255) NOT NULL COMMENT '圈子简介',
    icon           VARCHAR(20)  NOT NULL DEFAULT 'TAG' COMMENT '圈子图标标识',
    owner_user_id  BIGINT       DEFAULT NULL COMMENT '创建人（圈主）编号',
    member_count   INT          NOT NULL DEFAULT 0 COMMENT '成员数量',
    create_time    DATETIME     NOT NULL COMMENT '创建时间',
    INDEX idx_circle_owner (owner_user_id),
    CONSTRAINT fk_circle_owner FOREIGN KEY (owner_user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='打卡圈子表';

-- -----------------------------------------------------------
-- 9. 圈子成员表
-- -----------------------------------------------------------
CREATE TABLE circle_member (
    id         BIGINT       PRIMARY KEY AUTO_INCREMENT COMMENT '成员编号',
    circle_id  BIGINT       NOT NULL COMMENT '圈子编号',
    user_id    BIGINT       NOT NULL COMMENT '用户编号',
    role       VARCHAR(20)  NOT NULL DEFAULT 'MEMBER' COMMENT '角色：OWNER/MEMBER',
    join_time  DATETIME     NOT NULL COMMENT '加入时间',
    INDEX idx_cm_circle (circle_id),
    INDEX idx_cm_user (user_id),
    CONSTRAINT fk_circle_member_circle FOREIGN KEY (circle_id) REFERENCES social_circle(id),
    CONSTRAINT fk_circle_member_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='圈子成员表';

-- -----------------------------------------------------------
-- 10. 圈子帖子表
-- -----------------------------------------------------------
CREATE TABLE circle_post (
    id          BIGINT        PRIMARY KEY AUTO_INCREMENT COMMENT '帖子编号',
    circle_id   BIGINT        NOT NULL COMMENT '所属圈子编号',
    user_id     BIGINT        NOT NULL COMMENT '发帖人编号',
    check_in_id BIGINT        DEFAULT NULL COMMENT '关联打卡编号（打卡分享类型）',
    visibility  VARCHAR(20)   NOT NULL DEFAULT 'PUBLIC' COMMENT '可见性：PUBLIC/MEMBER_ONLY',
    post_type   VARCHAR(30)   NOT NULL DEFAULT 'NORMAL' COMMENT '帖子类型：NORMAL/CHECKIN_SHARE',
    content     VARCHAR(1000) NOT NULL COMMENT '帖子内容',
    create_time DATETIME      NOT NULL COMMENT '发布时间',
    INDEX idx_post_circle (circle_id),
    INDEX idx_post_user (user_id),
    INDEX idx_post_checkin (check_in_id),
    CONSTRAINT fk_post_circle FOREIGN KEY (circle_id) REFERENCES social_circle(id),
    CONSTRAINT fk_post_user FOREIGN KEY (user_id) REFERENCES user(id),
    CONSTRAINT fk_post_checkin FOREIGN KEY (check_in_id) REFERENCES check_in(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='圈子帖子表';

-- -----------------------------------------------------------
-- 11. 帖子点赞表
-- -----------------------------------------------------------
CREATE TABLE post_like (
    id          BIGINT   PRIMARY KEY AUTO_INCREMENT COMMENT '点赞编号',
    post_id     BIGINT   NOT NULL COMMENT '帖子编号',
    user_id     BIGINT   NOT NULL COMMENT '点赞用户编号',
    create_time DATETIME NOT NULL COMMENT '点赞时间',
    INDEX idx_like_post (post_id),
    INDEX idx_like_user (user_id),
    CONSTRAINT fk_like_post FOREIGN KEY (post_id) REFERENCES circle_post(id),
    CONSTRAINT fk_like_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子点赞表';

-- -----------------------------------------------------------
-- 12. 帖子评论表
-- -----------------------------------------------------------
CREATE TABLE post_comment (
    id          BIGINT   PRIMARY KEY AUTO_INCREMENT COMMENT '评论编号',
    post_id     BIGINT   NOT NULL COMMENT '帖子编号',
    user_id     BIGINT   NOT NULL COMMENT '评论用户编号',
    content     TEXT     NOT NULL COMMENT '评论内容',
    create_time DATETIME NOT NULL COMMENT '评论时间',
    INDEX idx_comment_post (post_id),
    INDEX idx_comment_user (user_id),
    CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES circle_post(id),
    CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子评论表';

-- -----------------------------------------------------------
-- 13. 私信表
-- -----------------------------------------------------------
CREATE TABLE direct_message (
    id          BIGINT   PRIMARY KEY AUTO_INCREMENT COMMENT '私信编号',
    sender_id   BIGINT   NOT NULL COMMENT '发送方用户编号',
    receiver_id BIGINT   NOT NULL COMMENT '接收方用户编号',
    content     TEXT     NOT NULL COMMENT '私信内容',
    create_time DATETIME NOT NULL COMMENT '发送时间',
    INDEX idx_dm_sender (sender_id),
    INDEX idx_dm_receiver (receiver_id),
    CONSTRAINT fk_dm_sender FOREIGN KEY (sender_id) REFERENCES user(id),
    CONSTRAINT fk_dm_receiver FOREIGN KEY (receiver_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='私信表';

-- ============================================================
-- 初始种子数据
-- ============================================================

-- 勋章种子数据
INSERT INTO badge (code, name, description, condition_text) VALUES
('FIRST_CHECK_IN', '初次打卡勋章', '完成第一次目标打卡，开启自律记录。', '累计完成打卡 1 次'),
('STREAK_7', '连续7天勋章', '连续坚持一周，形成稳定节奏。', '连续打卡 7 天'),
('STREAK_30', '连续30天勋章', '连续坚持一个月，习惯已经成型。', '连续打卡 30 天'),
('CHECK_IN_100', '百次打卡勋章', '累计完成一百次打卡，长期执行力突出。', '累计完成打卡 100 次'),
('DISCIPLINE_MASTER', '自律达人勋章', '兼具长期积累和连续坚持的综合奖励。', '累计 100 次且连续 30 天');

-- 默认圈子种子数据
INSERT INTO social_circle (name, description, icon, owner_user_id, member_count, create_time) VALUES
('英语打卡圈', '记录背单词、口语练习、阅读训练，和同伴一起保持输入输出。', 'EN', NULL, 0, NOW()),
('健身打卡圈', '分享训练计划、跑步记录和饮食控制，让运动习惯更稳定。', 'FIT', NULL, 0, NOW()),
('阅读打卡圈', '沉淀每日阅读页数、读书笔记和阶段复盘。', 'READ', NULL, 0, NOW());
