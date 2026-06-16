from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..common import AppException, ok
from ..deps import get_current_user, get_db
from ..models import User
from ..schemas import PasswordRequest, ProfileRequest, user_profile
from ..security import hash_password, verify_password

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return ok(user_profile(current_user))


@router.put("/profile")
def update_profile(
    request: ProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = (
        db.query(User)
        .filter(User.username == request.username, User.id != current_user.id)
        .first()
    )
    if exists is not None:
        raise AppException("用户名已存在")
    current_user.username = request.username
    current_user.email = request.email
    db.commit()
    db.refresh(current_user)
    return ok(user_profile(current_user))


@router.put("/password")
def change_password(
    request: PasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(request.oldPassword, current_user.password):
        raise AppException("原密码错误")
    current_user.password = hash_password(request.newPassword)
    db.commit()
    return ok()
