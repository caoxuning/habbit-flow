from fastapi import Depends, Header
from sqlalchemy.orm import Session

from .common import AppException
from .database import SessionLocal
from .models import User
from .security import parse_user_id


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppException("登录状态已失效", 401)
    user_id = parse_user_id(authorization[7:])
    user = db.get(User, user_id)
    if user is None:
        raise AppException("登录状态已失效", 401)
    return user
