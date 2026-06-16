from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..common import AppException, ok
from ..deps import get_db
from ..models import User
from ..schemas import AuthRequest, user_profile
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register")
def register(request: AuthRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == request.username).first()
    if exists is not None:
        raise AppException("用户名已存在")
    user = User(
        username=request.username,
        password=hash_password(request.password),
        email=request.email,
        create_time=datetime.now(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ok({"token": create_access_token(user.id), "profile": user_profile(user)})


@router.post("/login")
def login(request: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if user is None or not verify_password(request.password, user.password):
        raise AppException("用户名或密码错误")
    return ok({"token": create_access_token(user.id), "profile": user_profile(user)})
