from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..common import ok
from ..deps import get_current_user, get_db
from ..models import Badge, User, UserBadge
from ..schemas import badge_dict

router = APIRouter(prefix="/api/badges", tags=["勋章"])


@router.get("/mine")
def my_badges(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Badge, UserBadge)
        .join(UserBadge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.obtained_time.desc())
        .all()
    )
    return ok([badge_dict(badge, user_badge.obtained_time) for badge, user_badge in rows])
