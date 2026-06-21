# HabitFlow 自律目标追踪平台

HabitFlow 是一个前后端分离的习惯养成与自律目标管理系统，当前以个人目标管理闭环为核心，覆盖用户认证、目标管理、每日打卡、补卡、数据统计、勋章奖励和可视化报表。项目后续可继续扩展好友、圈子、动态流、消息提醒和排行榜等社交功能。

## 技术栈

- 前端：Vue 3、Element Plus、Axios、ECharts、Vite
- 后端：Python、FastAPI、SQLAlchemy、JWT、Passlib BCrypt
- 数据库：MySQL

## 目录结构

```text
HabitFlow
├─ backend_fastapi       FastAPI 后端
├─ frontend              Vue3 前端
├─ database
│  └─ schema.sql         MySQL 建库建表脚本
├─ docs
│  ├─ api
│  │  └─ HabitFlow统一接口文档.md
│  └─ 三人功能分工安排.md
└─ HabitFlow功能设计清单.md
```

说明：原 `backend/` Java 后端目录已删除，当前以后端目录 `backend_fastapi/` 为准。

## 当前已实现功能

- 用户管理：注册、登录、个人信息维护、修改密码
- 目标管理：创建、编辑、删除、设置周期、设置每日目标次数、状态管理
- 打卡管理：今日打卡、快速打卡、重复打卡校验、补卡、打卡记录查看
- 数据统计：目标总数、进行中目标数、总打卡次数、连续打卡天数、平均完成率
- 可视化报表：月度成长柱状图、目标完成率图表
- 勋章奖励：初次打卡、连续 7 天、连续 30 天、百次打卡、自律达人

## 待扩展功能

- 好友管理：用户搜索、好友申请、好友列表
- 圈子功能：圈子列表、创建圈子、加入圈子、退出圈子
- 动态流：圈内发帖、帖子列表、我的圈子动态
- 消息提醒：每日打卡提醒、目标到期提醒、连续中断提醒、消息中心
- 排行榜：好友排行榜、圈子排行榜、目标类型排行榜
- 互动增强：评论、点赞、日历热力图

## 文档入口

- 功能设计：[HabitFlow功能设计清单.md](HabitFlow功能设计清单.md)
- 三人分工：[docs/三人功能分工安排.md](docs/三人功能分工安排.md)
- 统一接口文档：[docs/api/HabitFlow统一接口文档.md](docs/api/HabitFlow统一接口文档.md)
- FastAPI 后端说明：[backend_fastapi/README.md](backend_fastapi/README.md)
- FastAPI 已完成功能：[backend_fastapi/已完成功能.md](backend_fastapi/已完成功能.md)

## 数据库初始化

1. 启动 MySQL。
2. 执行数据库脚本：

```bash
mysql -u root -p < database/schema.sql
```

3. 后端默认数据库连接为：

```text
mysql+pymysql://root:root@localhost:3306/habitflow?charset=utf8mb4
```

如需修改数据库连接，可在启动后端前设置环境变量：

```bash
set DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/habitflow?charset=utf8mb4
```

## 启动后端

进入后端目录：

```bash
cd backend_fastapi
```

创建并激活虚拟环境：

```bash
py -m venv .venv
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

后端默认地址：

```text
http://localhost:8081
```

接口文档地址：

```text
http://localhost:8081/docs
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

Vite 已配置 `/api` 代理到：

```text
http://localhost:8081
```

## 构建检查

前端构建：

```bash
cd frontend
npm.cmd run build
```

后端接口检查：

```bash
cd backend_fastapi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

启动后访问：

```text
http://localhost:8081/docs
```

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

社交、消息、排行榜等待扩展接口见 [docs/api/HabitFlow统一接口文档.md](docs/api/HabitFlow统一接口文档.md)。

## 关键业务算法

目标完成率：

```text
完成率 = 已完成打卡次数 / 应完成打卡次数 * 100%
```

连续打卡天数：

```text
系统按用户已完成打卡日期去重，从当天开始向前逐日检查，遇到断档日期停止计算。
```

勋章自动发放：

```text
每次打卡或补卡成功后执行勋章规则判断，满足条件且未获得过该勋章时写入 user_badge 表。
```

## 推荐开发顺序

| 阶段 | 内容 |
| --- | --- |
| 第一阶段 | 注册登录、目标管理、今日打卡、补卡、打卡记录、数据概览、勋章奖励 |
| 第二阶段 | 用户搜索、好友申请、好友列表、圈子列表、加入圈子、圈内发帖、社区动态流 |
| 第三阶段 | 消息提醒、排行榜、评论点赞、日历热力图、测试用例、文档和 PPT |

如果课程设计时间紧，优先保证第一阶段个人功能闭环可稳定演示，再补齐第二阶段社交基础闭环。
