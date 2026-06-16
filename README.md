# HabitFlow 自律目标追踪平台

HabitFlow 是一个前后端分离的轻量化习惯养成与目标管理系统，覆盖用户认证、目标管理、每日打卡、补卡、数据统计、勋章奖励和可视化报表。

## 技术栈

- 前端：Vue3、Element Plus、Axios、ECharts、Vite
- 后端：Spring Boot 3、MyBatis Plus、JWT、BCrypt
- 数据库：MySQL

## 目录结构

```text
HabitFlow
├─ backend              Spring Boot 后端
├─ frontend             Vue3 前端
└─ database
   └─ schema.sql        MySQL 建库建表与勋章初始化脚本
```

## 功能模块

- 用户管理：注册、登录、个人信息维护、修改密码
- 目标管理：创建、编辑、删除、设置周期、设置每日目标次数
- 打卡管理：每日打卡、重复打卡校验、补卡、连续打卡统计
- 数据统计：总完成次数、连续天数、目标完成率、月度成长报表、图表展示
- 勋章奖励：初次打卡、连续 7 天、连续 30 天、百次打卡、自律达人
- 消息提醒：前端预留提醒入口，后端可扩展定时任务或消息表

## 数据库初始化

1. 启动 MySQL。
2. 执行脚本：

```bash
mysql -u root -p < database/schema.sql
```

3. 如本机账号密码不是 `root/root`，修改 [application.yml](backend/src/main/resources/application.yml:8) 中的 `spring.datasource.username` 和 `spring.datasource.password`。

## 启动后端

```bash
cd backend
mvn spring-boot:run
```

后端默认地址：

```text
http://localhost:8080
```

## 启动前端

PowerShell 如遇到 npm 执行策略限制，可使用 `npm.cmd`：

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

前端默认地址：

```text
http://localhost:5173
```

Vite 已配置 `/api` 代理到 `http://localhost:8080`。

## 核心接口

| 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 认证 | POST | `/api/auth/register` | 用户注册 |
| 认证 | POST | `/api/auth/login` | 用户登录 |
| 用户 | GET | `/api/user/profile` | 获取个人信息 |
| 用户 | PUT | `/api/user/profile` | 修改个人信息 |
| 用户 | PUT | `/api/user/password` | 修改密码 |
| 目标 | GET | `/api/goals` | 目标列表与完成率 |
| 目标 | POST | `/api/goals` | 创建目标 |
| 目标 | PUT | `/api/goals/{goalId}` | 编辑目标 |
| 目标 | DELETE | `/api/goals/{goalId}` | 删除目标 |
| 打卡 | GET | `/api/check-ins` | 打卡记录 |
| 打卡 | POST | `/api/check-ins` | 今日打卡 |
| 打卡 | POST | `/api/check-ins/makeup` | 补卡 |
| 统计 | GET | `/api/stats/dashboard` | 仪表盘统计 |
| 勋章 | GET | `/api/badges/mine` | 我的勋章 |

## 关键业务算法

目标完成率：

```text
完成率 = 已完成打卡次数 / 应完成打卡次数 * 100%
```

连续打卡天数：

系统按用户已完成打卡日期去重，从当天开始向前逐日检查，直到遇到断档日期。

勋章自动发放：

每次打卡或补卡成功后执行勋章规则判断，满足条件且未获得过该勋章时写入 `user_badge` 表。

## 项目实施计划

| 阶段 | 时间 | 内容 |
| --- | --- | --- |
| 第一阶段 | 第 1-3 天 | 需求分析、数据库设计、原型设计 |
| 第二阶段 | 第 4-8 天 | 后端接口开发、数据库实现、用户认证模块开发 |
| 第三阶段 | 第 9-11 天 | 前端页面开发、数据可视化开发、功能联调 |
| 第四阶段 | 第 12-14 天 | 系统测试、Bug 修复、文档编写、PPT 制作与答辩准备 |

## 可继续扩展

- 增加消息提醒表与 Spring 定时任务，实现每日提醒、逾期提醒、连续中断提醒。
- 增加补卡审核状态，实现“申请-审核-生效”的流程。
- 增加目标类型字典表，统一维护运动、学习、阅读等分类。
- 增加单元测试和接口测试，覆盖打卡校验、完成率和勋章发放规则。
