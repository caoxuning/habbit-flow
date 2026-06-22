# 数据库持久化与表结构 PlantUML

## 当前是否支持持久化

当前后端使用 MySQL 持久化存储，不是内存数据库。数据库连接来自环境变量 `DATABASE_URL`：

```text
mysql+pymysql://用户名:密码@主机:3306/habitflow?charset=utf8mb4
```

如果没有设置环境变量，代码默认连接：

```text
mysql+pymysql://root:1234@localhost:3306/habitflow?charset=utf8mb4
```

所以理论上，只要连接的是同一个 MySQL 数据库，用户、目标、打卡、好友、圈子、聊天等数据都会保留。

## 为什么会感觉数据丢了

常见原因有四个：

1. 后端连接到了不同数据库。
   - 例如有时用 `root:123456`，有时走默认 `root:1234`。
   - 或者一会儿连本地 MySQL，一会儿连服务器 MySQL。

2. 运行了演示数据重置脚本。
   - `backend_fastapi/scripts/seed_demo_data.py --reset-demo` 会删除并重建固定演示账号相关数据。
   - 受影响账号包括 `demo_admin`、`member1`、`member2`、`member3`。

3. 使用了不同账号登录。
   - 目标、打卡、勋章、好友、圈子加入关系都是按用户隔离的。

4. 前端缓存的是旧 token。
   - 切换数据库后，旧 token 中的用户 id 可能在新数据库里不存在或对应不同数据。
   - 这种情况建议退出登录后重新登录。

## 后续服务器共同访问方案

推荐部署方式：

1. 在服务器上部署 MySQL。
2. 创建 `habitflow` 数据库。
3. 创建专用数据库账号，不要共享 root。
4. 后端服务统一设置同一个 `DATABASE_URL`。
5. 所有成员访问同一个后端地址，或本地后端都连同一个服务器 MySQL。

示例：

```text
mysql+pymysql://habitflow_user:强密码@服务器IP:3306/habitflow?charset=utf8mb4
```

MySQL 初始化示例：

```sql
CREATE DATABASE IF NOT EXISTS habitflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'habitflow_user'@'%' IDENTIFIED BY '强密码';
GRANT ALL PRIVILEGES ON habitflow.* TO 'habitflow_user'@'%';
FLUSH PRIVILEGES;
```

## PlantUML 表结构图

```plantuml
@startuml HabitFlow_ER
hide circle
skinparam linetype ortho
skinparam classAttributeIconSize 0

entity "user" as user {
  * id : BIGINT <<PK>>
  --
  username : VARCHAR(50) <<UNIQUE>>
  password : VARCHAR(255)
  email : VARCHAR(120)
  create_time : DATETIME
}

entity "goal" as goal {
  * id : BIGINT <<PK>>
  --
  user_id : BIGINT <<FK>>
  name : VARCHAR(120)
  type : VARCHAR(50)
  start_date : DATE
  end_date : DATE
  cycle : VARCHAR(20)
  daily_target_count : INT
  priority : VARCHAR(20)
  status : VARCHAR(20)
  create_time : DATETIME
  update_time : DATETIME
}

entity "check_in" as check_in {
  * id : BIGINT <<PK>>
  --
  goal_id : BIGINT <<FK>>
  user_id : BIGINT <<FK>>
  check_date : DATE
  check_time : DATETIME
  status : VARCHAR(20)
  remark : VARCHAR(500)
  makeup : BOOLEAN
}

entity "badge" as badge {
  * id : BIGINT <<PK>>
  --
  code : VARCHAR(50) <<UNIQUE>>
  name : VARCHAR(80)
  description : VARCHAR(255)
  condition_text : VARCHAR(255)
}

entity "user_badge" as user_badge {
  * id : BIGINT <<PK>>
  --
  user_id : BIGINT <<FK>>
  badge_id : BIGINT <<FK>>
  obtained_time : DATETIME
}

entity "friendship" as friendship {
  * id : BIGINT <<PK>>
  --
  requester_id : BIGINT <<FK>>
  addressee_id : BIGINT <<FK>>
  status : VARCHAR(20)
  message : VARCHAR(255)
  create_time : DATETIME
  update_time : DATETIME
}

entity "direct_message" as direct_message {
  * id : BIGINT <<PK>>
  --
  sender_id : BIGINT <<FK>>
  receiver_id : BIGINT <<FK>>
  content : TEXT
  create_time : DATETIME
}

entity "social_circle" as social_circle {
  * id : BIGINT <<PK>>
  --
  name : VARCHAR(80) <<UNIQUE>>
  description : VARCHAR(255)
  icon : VARCHAR(20)
  owner_user_id : BIGINT <<FK, NULL>>
  member_count : INT
  create_time : DATETIME
}

entity "circle_member" as circle_member {
  * id : BIGINT <<PK>>
  --
  circle_id : BIGINT <<FK>>
  user_id : BIGINT <<FK>>
  role : VARCHAR(20)
  join_time : DATETIME
}

entity "circle_post" as circle_post {
  * id : BIGINT <<PK>>
  --
  circle_id : BIGINT <<FK>>
  user_id : BIGINT <<FK>>
  content : VARCHAR(1000)
  create_time : DATETIME
}

entity "post_like" as post_like {
  * id : BIGINT <<PK>>
  --
  post_id : BIGINT <<FK>>
  user_id : BIGINT <<FK>>
  create_time : DATETIME
}

entity "post_comment" as post_comment {
  * id : BIGINT <<PK>>
  --
  post_id : BIGINT <<FK>>
  user_id : BIGINT <<FK>>
  content : TEXT
  create_time : DATETIME
}

user ||--o{ goal : owns
user ||--o{ check_in : records
goal ||--o{ check_in : contains

user ||--o{ user_badge : earns
badge ||--o{ user_badge : granted_as

user ||--o{ friendship : requester
user ||--o{ friendship : addressee
user ||--o{ direct_message : sender
user ||--o{ direct_message : receiver

user ||--o{ social_circle : owns
social_circle ||--o{ circle_member : has
user ||--o{ circle_member : joins

social_circle ||--o{ circle_post : contains
user ||--o{ circle_post : publishes

circle_post ||--o{ post_like : receives
user ||--o{ post_like : creates

circle_post ||--o{ post_comment : has
user ||--o{ post_comment : writes
@enduml
```

