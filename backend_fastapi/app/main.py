from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text

from .business import seed_badges, seed_circles
from .common import install_exception_handlers
from .database import Base, SessionLocal, engine
from .routers import auth, badges, checkins, exports, goals, notifications, social, stats, users

app = FastAPI(title="HabitFlow FastAPI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_exception_handlers(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    message = first.get("msg", "参数校验失败")
    return JSONResponse(status_code=400, content={"code": 400, "message": message, "data": None})


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    ensure_goal_priority_column()
    ensure_circle_post_share_columns()
    ensure_notification_columns()
    db = SessionLocal()
    try:
        seed_badges(db)
        seed_circles(db)
    finally:
        db.close()


def ensure_goal_priority_column():
    inspector = inspect(engine)
    if "goal" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("goal")}
    if "priority" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE goal ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'NORMAL'"))


def ensure_circle_post_share_columns():
    inspector = inspect(engine)
    if "circle_post" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("circle_post")}
    statements = []
    if "check_in_id" not in columns:
        statements.append("ALTER TABLE circle_post ADD COLUMN check_in_id BIGINT NULL")
    if "visibility" not in columns:
        statements.append("ALTER TABLE circle_post ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'PUBLIC'")
    if "post_type" not in columns:
        statements.append("ALTER TABLE circle_post ADD COLUMN post_type VARCHAR(30) NOT NULL DEFAULT 'NORMAL'")
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_notification_columns():
    inspector = inspect(engine)
    if "notification" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("notification")}
    statements = []
    if "type" not in columns:
        statements.append("ALTER TABLE notification ADD COLUMN type VARCHAR(50) NOT NULL DEFAULT 'DAILY_CHECK_IN'")
    if "title" not in columns:
        statements.append("ALTER TABLE notification ADD COLUMN title VARCHAR(120) NOT NULL DEFAULT '消息提醒'")
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(checkins.router)
app.include_router(stats.router)
app.include_router(badges.router)
app.include_router(exports.router)
app.include_router(social.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"name": "HabitFlow FastAPI Backend", "docs": "/docs"}
