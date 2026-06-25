-- HabitFlow schema exported from the remote RDS database.
-- Schema only; table data is not included.
-- Field comments are added for local reading and database design documentation.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Table: badge
DROP TABLE IF EXISTS `badge`;
CREATE TABLE `badge` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '勋章主键，自增编号',
  `code` varchar(50) NOT NULL COMMENT '勋章唯一编码，供后端判断和发放使用',
  `name` varchar(80) NOT NULL COMMENT '勋章展示名称',
  `description` varchar(255) NOT NULL COMMENT '勋章说明文案',
  `condition_text` varchar(255) NOT NULL COMMENT '勋章解锁条件的展示文案',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='勋章定义表，保存系统内所有可获得的成就勋章';

-- Table: user
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户主键，自增编号',
  `username` varchar(50) NOT NULL COMMENT '用户名/展示名称，用于登录、好友、评论和聊天展示',
  `password` varchar(255) NOT NULL COMMENT '加密后的登录密码，不保存明文密码',
  `email` varchar(120) DEFAULT NULL COMMENT '用户邮箱，用于资料展示和联系信息',
  `create_time` datetime NOT NULL COMMENT '账号创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户账号表，保存登录和个人资料基础信息';

-- Table: goal
DROP TABLE IF EXISTS `goal`;
CREATE TABLE `goal` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '目标主键，自增编号',
  `user_id` bigint NOT NULL COMMENT '目标所属用户编号，关联 user.id',
  `name` varchar(120) NOT NULL COMMENT '目标名称，例如力量训练、英语听力精听',
  `type` varchar(50) NOT NULL COMMENT '目标分类，例如运动、英语、阅读、早睡',
  `start_date` date NOT NULL COMMENT '目标开始日期',
  `end_date` date NOT NULL COMMENT '目标结束日期',
  `cycle` varchar(20) NOT NULL COMMENT '目标周期，例如 DAILY、WEEKLY、MONTHLY',
  `daily_target_count` int NOT NULL COMMENT '每日计划完成次数或目标次数',
  `priority` varchar(20) NOT NULL COMMENT '目标重要程度，例如 NORMAL、IMPORTANT、URGENT',
  `status` varchar(20) NOT NULL COMMENT '目标状态，例如 ACTIVE、PAUSED、DONE',
  `create_time` datetime NOT NULL COMMENT '目标创建时间',
  `update_time` datetime NOT NULL COMMENT '目标最近更新时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `goal_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='习惯目标表，保存用户创建的长期或阶段性打卡目标';

-- Table: check_in
DROP TABLE IF EXISTS `check_in`;
CREATE TABLE `check_in` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '打卡记录主键，自增编号',
  `goal_id` bigint NOT NULL COMMENT '本次打卡对应的目标编号，关联 goal.id',
  `user_id` bigint NOT NULL COMMENT '打卡用户编号，关联 user.id',
  `check_date` date NOT NULL COMMENT '打卡所属日期，用于日历和每日统计',
  `check_time` datetime NOT NULL COMMENT '实际提交打卡的时间',
  `status` varchar(20) NOT NULL COMMENT '打卡状态，当前主要使用 DONE 表示已完成',
  `remark` varchar(500) DEFAULT NULL COMMENT '打卡备注，例如训练内容、学习进度、补充说明',
  `makeup` tinyint(1) NOT NULL COMMENT '是否为补卡记录，0 表示正常打卡，1 表示补卡',
  PRIMARY KEY (`id`),
  KEY `goal_id` (`goal_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `check_in_ibfk_1` FOREIGN KEY (`goal_id`) REFERENCES `goal` (`id`),
  CONSTRAINT `check_in_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='打卡记录表，保存用户每天完成目标的记录';

-- Table: social_circle
DROP TABLE IF EXISTS `social_circle`;
CREATE TABLE `social_circle` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '圈子主键，自增编号',
  `name` varchar(80) NOT NULL COMMENT '圈子名称，例如英语打卡小组、运动监督圈',
  `description` varchar(255) NOT NULL COMMENT '圈子简介，用于圈子广场展示',
  `icon` varchar(20) NOT NULL COMMENT '圈子图标标识，前端根据该值显示图标或样式',
  `owner_user_id` bigint DEFAULT NULL COMMENT '圈子创建者用户编号，关联 user.id',
  `member_count` int NOT NULL COMMENT '圈子当前成员数量',
  `create_time` datetime NOT NULL COMMENT '圈子创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `owner_user_id` (`owner_user_id`),
  CONSTRAINT `social_circle_ibfk_1` FOREIGN KEY (`owner_user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='社交圈子表，保存用户可加入的打卡圈子';

-- Table: circle_member
DROP TABLE IF EXISTS `circle_member`;
CREATE TABLE `circle_member` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '圈子成员关系主键，自增编号',
  `circle_id` bigint NOT NULL COMMENT '圈子编号，关联 social_circle.id',
  `user_id` bigint NOT NULL COMMENT '成员用户编号，关联 user.id',
  `role` varchar(20) NOT NULL COMMENT '成员角色，例如 OWNER、MEMBER',
  `join_time` datetime NOT NULL COMMENT '加入圈子的时间',
  PRIMARY KEY (`id`),
  KEY `circle_id` (`circle_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `circle_member_ibfk_1` FOREIGN KEY (`circle_id`) REFERENCES `social_circle` (`id`),
  CONSTRAINT `circle_member_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='圈子成员表，保存用户与圈子的加入关系';

-- Table: circle_post
DROP TABLE IF EXISTS `circle_post`;
CREATE TABLE `circle_post` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '圈子动态主键，自增编号',
  `circle_id` bigint NOT NULL COMMENT '动态所属圈子编号，关联 social_circle.id',
  `user_id` bigint NOT NULL COMMENT '动态发布者用户编号，关联 user.id',
  `check_in_id` bigint DEFAULT NULL COMMENT '关联的打卡记录编号，普通动态可为空',
  `visibility` varchar(20) NOT NULL COMMENT '动态可见范围，例如 PUBLIC、FRIENDS、CIRCLE、PRIVATE',
  `post_type` varchar(30) NOT NULL COMMENT '动态类型，例如普通发帖或打卡分享',
  `content` varchar(1000) NOT NULL COMMENT '动态正文内容',
  `create_time` datetime NOT NULL COMMENT '动态发布时间',
  PRIMARY KEY (`id`),
  KEY `circle_id` (`circle_id`),
  KEY `user_id` (`user_id`),
  KEY `check_in_id` (`check_in_id`),
  CONSTRAINT `circle_post_ibfk_1` FOREIGN KEY (`circle_id`) REFERENCES `social_circle` (`id`),
  CONSTRAINT `circle_post_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `circle_post_ibfk_3` FOREIGN KEY (`check_in_id`) REFERENCES `check_in` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='圈子动态表，保存圈子帖子和打卡分享内容';

-- Table: direct_message
DROP TABLE IF EXISTS `direct_message`;
CREATE TABLE `direct_message` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '私信消息主键，自增编号',
  `sender_id` bigint NOT NULL COMMENT '发送者用户编号，关联 user.id',
  `receiver_id` bigint NOT NULL COMMENT '接收者用户编号，关联 user.id',
  `content` text NOT NULL COMMENT '私信正文内容',
  `create_time` datetime NOT NULL COMMENT '消息发送时间',
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `receiver_id` (`receiver_id`),
  CONSTRAINT `direct_message_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`),
  CONSTRAINT `direct_message_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='好友私信表，保存好友之间的一对一聊天消息';

-- Table: friendship
DROP TABLE IF EXISTS `friendship`;
CREATE TABLE `friendship` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '好友申请/关系主键，自增编号',
  `requester_id` bigint NOT NULL COMMENT '发起好友申请的用户编号，关联 user.id',
  `addressee_id` bigint NOT NULL COMMENT '接收好友申请的用户编号，关联 user.id',
  `status` varchar(20) NOT NULL COMMENT '好友关系状态，例如 PENDING、ACCEPTED、REJECTED',
  `message` varchar(255) DEFAULT NULL COMMENT '好友申请留言',
  `create_time` datetime NOT NULL COMMENT '申请创建时间',
  `update_time` datetime NOT NULL COMMENT '关系状态最近更新时间',
  PRIMARY KEY (`id`),
  KEY `requester_id` (`requester_id`),
  KEY `addressee_id` (`addressee_id`),
  CONSTRAINT `friendship_ibfk_1` FOREIGN KEY (`requester_id`) REFERENCES `user` (`id`),
  CONSTRAINT `friendship_ibfk_2` FOREIGN KEY (`addressee_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='好友关系表，保存好友申请和好友关系状态';

-- Table: notification
DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '消息提醒主键，自增编号',
  `user_id` bigint NOT NULL COMMENT '提醒接收用户编号，关联 user.id',
  `type` varchar(50) NOT NULL COMMENT '提醒类型，例如 DAILY_CHECK_IN、GOAL_EXPIRE、STREAK_BREAK',
  `title` varchar(120) NOT NULL COMMENT '提醒标题',
  `content` varchar(500) NOT NULL COMMENT '提醒具体内容',
  `is_read` tinyint(1) NOT NULL COMMENT '是否已读，0 表示未读，1 表示已读',
  `create_time` datetime NOT NULL COMMENT '提醒生成时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='消息提醒表，保存打卡提醒、到期预警和连续中断提醒';

-- Table: post_comment
DROP TABLE IF EXISTS `post_comment`;
CREATE TABLE `post_comment` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '评论主键，自增编号',
  `post_id` bigint NOT NULL COMMENT '被评论的动态编号，关联 circle_post.id',
  `user_id` bigint NOT NULL COMMENT '评论用户编号，关联 user.id',
  `content` text NOT NULL COMMENT '评论正文内容',
  `create_time` datetime NOT NULL COMMENT '评论发布时间',
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `post_comment_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `circle_post` (`id`),
  CONSTRAINT `post_comment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='动态评论表，保存圈子动态下的评论内容';

-- Table: post_like
DROP TABLE IF EXISTS `post_like`;
CREATE TABLE `post_like` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '点赞主键，自增编号',
  `post_id` bigint NOT NULL COMMENT '被点赞的动态编号，关联 circle_post.id',
  `user_id` bigint NOT NULL COMMENT '点赞用户编号，关联 user.id',
  `create_time` datetime NOT NULL COMMENT '点赞时间',
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `post_like_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `circle_post` (`id`),
  CONSTRAINT `post_like_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='动态点赞表，保存用户对圈子动态的点赞记录';

-- Table: user_badge
DROP TABLE IF EXISTS `user_badge`;
CREATE TABLE `user_badge` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户勋章关系主键，自增编号',
  `user_id` bigint NOT NULL COMMENT '获得勋章的用户编号，关联 user.id',
  `badge_id` bigint NOT NULL COMMENT '获得的勋章编号，关联 badge.id',
  `obtained_time` datetime NOT NULL COMMENT '勋章获得时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `badge_id` (`badge_id`),
  CONSTRAINT `user_badge_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `user_badge_ibfk_2` FOREIGN KEY (`badge_id`) REFERENCES `badge` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户勋章表，保存用户已经获得的勋章记录';

SET FOREIGN_KEY_CHECKS = 1;
