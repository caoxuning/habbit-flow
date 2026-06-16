# HabitFlow FastAPI 后端

这是基于现有 Java 后端功能整理出的 Python + FastAPI 版本，接口路径尽量保持与现有前端一致。

## 启动方式

```bash
cd backend_fastapi
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

默认数据库连接：

```text
mysql+pymysql://root:root@localhost:3306/habitflow?charset=utf8mb4
```

如需修改数据库连接：

```bash
set DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/habitflow?charset=utf8mb4
```

## 接口说明

接口统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

启动后可访问接口文档：

```text
http://localhost:8081/docs
```
