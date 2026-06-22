from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .business import seed_badges, seed_circles
from .common import install_exception_handlers
from .database import Base, SessionLocal, engine
from .routers import auth, badges, checkins, exports, goals, social, stats, users

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
    db = SessionLocal()
    try:
        seed_badges(db)
        seed_circles(db)
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(checkins.router)
app.include_router(stats.router)
app.include_router(badges.router)
app.include_router(exports.router)
app.include_router(social.router)


@app.get("/")
def root():
    return {"name": "HabitFlow FastAPI Backend", "docs": "/docs"}
