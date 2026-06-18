# HabitFlow 统一接口文档

版本：v1.0  
适用对象：前端开发、后端开发、成员三社交模块开发、联调测试  
后端地址：`http://localhost:8081`  
前端代理前缀：`/api`

## 1. 通用约定

### 1.1 请求地址

前端调用时统一使用 `/api` 开头，例如：

```text
GET /api/user/profile
```

本地后端真实地址为：

```text
http://localhost:8081/api/user/profile
```

### 1.2 登录认证

除注册、登录接口外，其他接口默认需要登录。

请求头格式：

```http
Authorization: Bearer <token>
```

### 1.3 统一返回格式

成功：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 400,
  "message": "错误说明",
  "data": null
}
```

### 1.4 常用错误码

| code | 说明 |
| --- | --- |
| 200 | 请求成功 |
| 400 | 参数错误或业务校验失败 |
| 401 | 未登录或登录状态失效 |
| 403 | 无权限操作 |
| 404 | 数据不存在 |
| 500 | 服务器内部错误 |

### 1.5 时间和枚举约定

日期格式：

```text
YYYY-MM-DD
```

时间格式：

```text
YYYY-MM-DDTHH:mm:ss
```

目标周期 `cycle`：

| 值 | 含义 |
| --- | --- |
| DAILY | 每日 |
| WEEKLY | 每周 |
| MONTHLY | 每月 |

目标状态 `status`：

| 值 | 含义 |
| --- | --- |
| ACTIVE | 进行中 |
| PAUSED | 已暂停 |
| DONE | 已完成 |

好友申请状态 `friendshipStatus`：

| 值 | 含义 |
| --- | --- |
| PENDING | 待处理 |
| ACCEPTED | 已通过 |
| REJECTED | 已拒绝 |

消息类型 `notificationType`：

| 值 | 含义 |
| --- | --- |
| DAILY_CHECK_IN | 每日打卡提醒 |
| GOAL_EXPIRE | 目标到期提醒 |
| STREAK_BREAK | 连续中断提醒 |
| FRIEND_REQUEST | 好友申请提醒 |
| CIRCLE_POST | 圈子动态提醒 |
| SYSTEM | 系统消息 |

## 2. 已实现接口

本节为当前 `backend_fastapi` 已实现接口，可直接联调。

## 2.1 认证接口

### 用户注册

```http
POST /api/auth/register
```

是否需要登录：否

请求体：

```json
{
  "username": "alice",
  "password": "123456",
  "email": "alice@example.com"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "jwt-token",
    "profile": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "createTime": "2026-06-18T12:00:00"
    }
  }
}
```

业务规则：

- 用户名不能为空。
- 密码不能为空。
- 用户名不能重复。
- 注册成功后直接返回 token。

### 用户登录

```http
POST /api/auth/login
```

是否需要登录：否

请求体：

```json
{
  "username": "alice",
  "password": "123456"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "jwt-token",
    "profile": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "createTime": "2026-06-18T12:00:00"
    }
  }
}
```

业务规则：

- 用户名或密码错误时返回业务错误。

## 2.2 用户接口

### 获取个人信息

```http
GET /api/user/profile
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "createTime": "2026-06-18T12:00:00"
  }
}
```

### 修改个人信息

```http
PUT /api/user/profile
```

是否需要登录：是

请求体：

```json
{
  "username": "alice_new",
  "email": "alice_new@example.com"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "alice_new",
    "email": "alice_new@example.com",
    "createTime": "2026-06-18T12:00:00"
  }
}
```

业务规则：

- 新用户名不能为空。
- 新用户名不能和其他用户重复。

### 修改密码

```http
PUT /api/user/password
```

是否需要登录：是

请求体：

```json
{
  "oldPassword": "123456",
  "newPassword": "654321"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 原密码必须正确。
- 新密码不能为空。

## 2.3 目标接口

### 目标列表

```http
GET /api/goals
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "goal": {
        "id": 1,
        "userId": 1,
        "name": "每天阅读",
        "type": "阅读",
        "startDate": "2026-06-01",
        "endDate": "2026-06-30",
        "cycle": "DAILY",
        "dailyTargetCount": 1,
        "status": "ACTIVE",
        "createTime": "2026-06-18T12:00:00",
        "updateTime": "2026-06-18T12:00:00"
      },
      "completedCount": 5,
      "expectedCount": 18,
      "completionRate": 27.8,
      "currentStreakDays": 3
    }
  ]
}
```

### 创建目标

```http
POST /api/goals
```

是否需要登录：是

请求体：

```json
{
  "name": "每天阅读",
  "type": "阅读",
  "startDate": "2026-06-01",
  "endDate": "2026-06-30",
  "cycle": "DAILY",
  "dailyTargetCount": 1,
  "status": "ACTIVE"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "userId": 1,
    "name": "每天阅读",
    "type": "阅读",
    "startDate": "2026-06-01",
    "endDate": "2026-06-30",
    "cycle": "DAILY",
    "dailyTargetCount": 1,
    "status": "ACTIVE",
    "createTime": "2026-06-18T12:00:00",
    "updateTime": "2026-06-18T12:00:00"
  }
}
```

业务规则：

- 目标名称、类型、开始日期、结束日期、周期不能为空。
- `dailyTargetCount` 必须大于等于 1。
- 结束日期不能早于开始日期。

### 编辑目标

```http
PUT /api/goals/{goalId}
```

是否需要登录：是

请求体同创建目标。

返回同创建目标。

业务规则：

- 只能编辑自己的目标。
- 目标不存在返回 404。

### 删除目标

```http
DELETE /api/goals/{goalId}
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 只能删除自己的目标。
- 删除目标时同步删除该目标相关打卡记录。

## 2.4 打卡接口

### 打卡记录列表

```http
GET /api/check-ins
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| goalId | number | 否 | 按目标筛选 |

示例：

```text
GET /api/check-ins?goalId=1
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "goalId": 1,
      "userId": 1,
      "checkDate": "2026-06-18",
      "checkTime": "2026-06-18T12:30:00",
      "status": "DONE",
      "remark": "完成阅读 30 分钟",
      "makeup": false
    }
  ]
}
```

### 今日打卡

```http
POST /api/check-ins
```

是否需要登录：是

请求体：

```json
{
  "goalId": 1,
  "remark": "完成阅读 30 分钟"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "goalId": 1,
    "userId": 1,
    "checkDate": "2026-06-18",
    "checkTime": "2026-06-18T12:30:00",
    "status": "DONE",
    "remark": "完成阅读 30 分钟",
    "makeup": false
  }
}
```

业务规则：

- 目标必须存在且属于当前用户。
- 目标状态必须为 `ACTIVE`。
- 只能提交当天打卡。
- 同一目标同一天不能重复打卡。
- 打卡日期必须在目标周期内。
- 打卡成功后自动检查并发放勋章。

### 补卡

```http
POST /api/check-ins/makeup
```

是否需要登录：是

请求体：

```json
{
  "goalId": 1,
  "checkDate": "2026-06-17",
  "remark": "昨天忘记提交，实际已完成"
}
```

返回同今日打卡，`makeup` 为 `true`。

业务规则：

- 补卡日期必须早于今天。
- 补卡日期必须在目标周期内。
- 同一目标同一天不能重复补卡或打卡。

## 2.5 统计接口

### 数据概览

```http
GET /api/stats/dashboard
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "totalGoals": 3,
    "activeGoals": 2,
    "totalCheckIns": 18,
    "currentStreakDays": 5,
    "averageCompletionRate": 61.5,
    "monthlyReport": [
      {
        "month": "2026-01",
        "count": 0
      },
      {
        "month": "2026-02",
        "count": 3
      }
    ],
    "goalProgress": [
      {
        "goal": {
          "id": 1,
          "userId": 1,
          "name": "每天阅读",
          "type": "阅读",
          "startDate": "2026-06-01",
          "endDate": "2026-06-30",
          "cycle": "DAILY",
          "dailyTargetCount": 1,
          "status": "ACTIVE",
          "createTime": "2026-06-18T12:00:00",
          "updateTime": "2026-06-18T12:00:00"
        },
        "completedCount": 5,
        "expectedCount": 18,
        "completionRate": 27.8,
        "currentStreakDays": 3
      }
    ]
  }
}
```

## 2.6 勋章接口

### 我的勋章

```http
GET /api/badges/mine
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "code": "FIRST_CHECK_IN",
      "name": "初次打卡勋章",
      "description": "完成第一次目标打卡，开启自律记录。",
      "conditionText": "累计完成打卡 1 次",
      "obtainedTime": "2026-06-18T12:30:00"
    }
  ]
}
```

## 3. 成员三待实现接口

本节为社交、消息、排行榜功能的统一约定接口。前端可以先按这些接口开发页面和 API 封装，后端后续按本文档实现。

## 3.1 用户搜索与好友接口

### 搜索用户

```http
GET /api/social/users/search
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| keyword | string | 是 | 用户名关键词 |

示例：

```text
GET /api/social/users/search?keyword=ali
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 2,
      "username": "alice",
      "email": "alice@example.com",
      "friendshipStatus": "NONE"
    }
  ]
}
```

业务规则：

- 搜索结果排除当前登录用户。
- `friendshipStatus` 可取 `NONE`、`PENDING`、`ACCEPTED`、`REJECTED`。

### 发送好友申请

```http
POST /api/social/friend-requests
```

是否需要登录：是

请求体：

```json
{
  "targetUserId": 2,
  "message": "一起坚持打卡吧"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "requester": {
      "id": 1,
      "username": "me",
      "email": "me@example.com"
    },
    "receiver": {
      "id": 2,
      "username": "alice",
      "email": "alice@example.com"
    },
    "message": "一起坚持打卡吧",
    "status": "PENDING",
    "createTime": "2026-06-18T12:00:00",
    "updateTime": "2026-06-18T12:00:00"
  }
}
```

业务规则：

- 不能添加自己。
- 不能重复发送待处理申请。
- 已经是好友时不能重复申请。

### 好友申请列表

```http
GET /api/social/friend-requests
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| type | string | 否 | `received` 收到的申请，`sent` 发出的申请，默认 `received` |

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "requester": {
        "id": 2,
        "username": "alice",
        "email": "alice@example.com"
      },
      "receiver": {
        "id": 1,
        "username": "me",
        "email": "me@example.com"
      },
      "message": "一起坚持打卡吧",
      "status": "PENDING",
      "createTime": "2026-06-18T12:00:00",
      "updateTime": "2026-06-18T12:00:00"
    }
  ]
}
```

### 接受好友申请

```http
PUT /api/social/friend-requests/{requestId}/accept
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 只有申请接收人可以接受申请。
- 只有 `PENDING` 状态可以接受。

### 拒绝好友申请

```http
PUT /api/social/friend-requests/{requestId}/reject
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 只有申请接收人可以拒绝申请。
- 只有 `PENDING` 状态可以拒绝。

### 好友列表

```http
GET /api/social/friends
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 2,
      "username": "alice",
      "email": "alice@example.com",
      "friendshipId": 1,
      "friendSince": "2026-06-18T12:00:00"
    }
  ]
}
```

## 3.2 圈子接口

### 圈子列表

```http
GET /api/social/circles
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| keyword | string | 否 | 圈子名称关键词 |
| joined | boolean | 否 | 是否只看我加入的圈子 |

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "英语打卡圈",
      "description": "一起坚持英语学习",
      "icon": "book",
      "ownerId": 1,
      "ownerName": "me",
      "memberCount": 12,
      "joined": true,
      "createTime": "2026-06-18T12:00:00"
    }
  ]
}
```

### 创建圈子

```http
POST /api/social/circles
```

是否需要登录：是

请求体：

```json
{
  "name": "阅读打卡圈",
  "description": "每天读一点，长期见变化",
  "icon": "reading"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 2,
    "name": "阅读打卡圈",
    "description": "每天读一点，长期见变化",
    "icon": "reading",
    "ownerId": 1,
    "ownerName": "me",
    "memberCount": 1,
    "joined": true,
    "createTime": "2026-06-18T12:00:00"
  }
}
```

业务规则：

- 圈子名称不能为空。
- 圈子名称不能重复。
- 创建者自动成为圈主和成员。

### 圈子详情

```http
GET /api/social/circles/{circleId}
```

是否需要登录：是

返回同圈子列表单项。

### 加入圈子

```http
POST /api/social/circles/{circleId}/join
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 圈子必须存在。
- 已加入时不能重复加入。

### 退出圈子

```http
DELETE /api/social/circles/{circleId}/leave
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 圈主不能直接退出自己创建的圈子。
- 未加入时不能退出。

### 圈子成员列表

```http
GET /api/social/circles/{circleId}/members
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "userId": 1,
      "username": "me",
      "email": "me@example.com",
      "role": "OWNER",
      "joinTime": "2026-06-18T12:00:00"
    }
  ]
}
```

成员角色 `role`：

| 值 | 含义 |
| --- | --- |
| OWNER | 圈主 |
| MEMBER | 普通成员 |

## 3.3 圈子帖子接口

### 发布帖子

```http
POST /api/social/circles/{circleId}/posts
```

是否需要登录：是

请求体：

```json
{
  "content": "今日英语阅读 30 分钟，完成打卡。"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "circleId": 1,
    "circleName": "英语打卡圈",
    "author": {
      "id": 1,
      "username": "me",
      "email": "me@example.com"
    },
    "content": "今日英语阅读 30 分钟，完成打卡。",
    "likeCount": 0,
    "commentCount": 0,
    "liked": false,
    "createTime": "2026-06-18T12:00:00"
  }
}
```

业务规则：

- 用户必须加入圈子后才能发帖。
- 帖子内容不能为空。

### 圈子帖子列表

```http
GET /api/social/circles/{circleId}/posts
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页条数，默认 10 |

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "circleId": 1,
        "circleName": "英语打卡圈",
        "author": {
          "id": 1,
          "username": "me",
          "email": "me@example.com"
        },
        "content": "今日英语阅读 30 分钟，完成打卡。",
        "likeCount": 0,
        "commentCount": 0,
        "liked": false,
        "createTime": "2026-06-18T12:00:00"
      }
    ],
    "page": 1,
    "pageSize": 10,
    "total": 1
  }
}
```

### 我的圈子动态流

```http
GET /api/social/feed
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页条数，默认 10 |

返回格式同圈子帖子列表。

业务规则：

- 返回当前用户已加入圈子的帖子。
- 按发布时间倒序排列。

### 删除自己的帖子

```http
DELETE /api/social/posts/{postId}
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

业务规则：

- 只能删除自己发布的帖子。

### 点赞帖子

```http
POST /api/social/posts/{postId}/like
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "liked": true,
    "likeCount": 1
  }
}
```

业务规则：

- 已点赞时再次调用可保持点赞状态，或按后端实现约定返回已点赞。

### 取消点赞

```http
DELETE /api/social/posts/{postId}/like
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "liked": false,
    "likeCount": 0
  }
}
```

### 评论帖子

```http
POST /api/social/posts/{postId}/comments
```

是否需要登录：是

请求体：

```json
{
  "content": "太棒了，继续坚持！"
}
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "postId": 1,
    "author": {
      "id": 2,
      "username": "alice",
      "email": "alice@example.com"
    },
    "content": "太棒了，继续坚持！",
    "createTime": "2026-06-18T12:10:00"
  }
}
```

### 评论列表

```http
GET /api/social/posts/{postId}/comments
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "postId": 1,
      "author": {
        "id": 2,
        "username": "alice",
        "email": "alice@example.com"
      },
      "content": "太棒了，继续坚持！",
      "createTime": "2026-06-18T12:10:00"
    }
  ]
}
```

## 3.4 消息提醒接口

### 消息列表

```http
GET /api/notifications
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| unreadOnly | boolean | 否 | 是否只看未读消息 |
| page | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页条数，默认 10 |

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "type": "DAILY_CHECK_IN",
        "title": "今日打卡提醒",
        "content": "你还有 2 个目标今天未打卡。",
        "read": false,
        "createTime": "2026-06-18T09:00:00"
      }
    ],
    "page": 1,
    "pageSize": 10,
    "total": 1,
    "unreadCount": 1
  }
}
```

### 未读消息数量

```http
GET /api/notifications/unread-count
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "unreadCount": 3
  }
}
```

### 标记单条消息已读

```http
PUT /api/notifications/{notificationId}/read
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

### 全部标记已读

```http
PUT /api/notifications/read-all
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

### 删除消息

```http
DELETE /api/notifications/{notificationId}
```

是否需要登录：是

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

## 3.5 排行榜接口

### 好友排行榜

```http
GET /api/rankings/friends
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| range | string | 否 | `TODAY`、`WEEK`、`MONTH`、`TOTAL`，默认 `WEEK` |

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "rank": 1,
      "userId": 2,
      "username": "alice",
      "checkInCount": 12,
      "currentStreakDays": 7,
      "checkedToday": true
    }
  ]
}
```

业务规则：

- 排行范围包括当前用户和好友。
- 默认按 `checkInCount` 降序排列。

### 圈子排行榜

```http
GET /api/rankings/circles/{circleId}
```

是否需要登录：是

查询参数同好友排行榜。

返回格式同好友排行榜。

业务规则：

- 只统计该圈子的成员。
- 用户需要加入圈子后才可查看。

### 目标类型排行榜

```http
GET /api/rankings/goal-types
```

是否需要登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| type | string | 是 | 目标类型，例如 阅读、运动、英语 |
| range | string | 否 | `TODAY`、`WEEK`、`MONTH`、`TOTAL`，默认 `WEEK` |

返回格式同好友排行榜。

## 4. 前端 API 封装建议

建议前端按模块拆分 API：

```text
authApi
userApi
goalApi
checkInApi
statsApi
badgeApi
socialApi
notificationApi
rankingApi
```

成员三开发时可优先实现：

- `socialApi.searchUsers`
- `socialApi.friends`
- `socialApi.friendRequests`
- `socialApi.requestFriend`
- `socialApi.acceptFriend`
- `socialApi.rejectFriend`
- `socialApi.circles`
- `socialApi.createCircle`
- `socialApi.joinCircle`
- `socialApi.leaveCircle`
- `socialApi.posts`
- `socialApi.publishPost`
- `socialApi.feed`
- `notificationApi.list`
- `notificationApi.unreadCount`
- `rankingApi.friendRanking`
- `rankingApi.circleRanking`

## 5. 成员三开发优先级

优先级一：社交基础闭环

- 用户搜索
- 发送好友申请
- 好友申请列表
- 接受或拒绝好友申请
- 好友列表

优先级二：圈子基础闭环

- 圈子列表
- 创建圈子
- 加入圈子
- 退出圈子
- 圈子详情
- 圈内发帖
- 圈子帖子列表
- 我的圈子动态流

优先级三：答辩增强

- 消息中心
- 好友排行榜
- 圈子排行榜
- 帖子点赞
- 帖子评论

如果时间紧，优先保证优先级一和优先级二可演示，优先级三可以作为拓展功能写入文档和答辩说明。
