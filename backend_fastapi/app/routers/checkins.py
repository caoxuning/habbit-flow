from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..business import evaluate_and_grant_badges
from ..common import AppException, ok
from ..deps import get_current_user, get_db
from ..models import CheckIn, Goal, User
from ..schemas import CheckInRequest, check_in_dict

router = APIRouter(prefix="/api/check-ins", tags=["打卡"])


def owned_goal(db: Session, user_id: int, goal_id: int) -> Goal:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if goal is None:
        raise AppException("目标不存在", 404)
    return goal


def save_check_in(
    db: Session,
    user_id: int,
    request: CheckInRequest,
    check_date: date,
    makeup: bool,
) -> CheckIn:
    goal = owned_goal(db, user_id, request.goalId)
    if goal.status != "ACTIVE":
        raise AppException("目标未处于进行中状态")
    if check_date < goal.start_date or check_date > goal.end_date:
        raise AppException("打卡日期不在目标周期内")
    exists = (
        db.query(CheckIn)
        .filter(
            CheckIn.user_id == user_id,
            CheckIn.goal_id == request.goalId,
            CheckIn.check_date == check_date,
        )
        .first()
    )
    if exists is not None:
        raise AppException("该目标当天已打卡")
    row = CheckIn(
        user_id=user_id,
        goal_id=request.goalId,
        check_date=check_date,
        check_time=datetime.now(),
        status="DONE",
        remark=request.remark,
        makeup=makeup,
    )
    db.add(row)
    db.flush()
    evaluate_and_grant_badges(db, user_id)
    db.commit()
    db.refresh(row)
    return row


@router.get("")
def list_checkins(
    goalId: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(CheckIn).filter(CheckIn.user_id == current_user.id)
    if goalId is not None:
        query = query.filter(CheckIn.goal_id == goalId)
    rows = query.order_by(CheckIn.check_date.desc(), CheckIn.check_time.desc()).all()
    return ok([check_in_dict(row) for row in rows])


@router.post("")
def check_in(
    request: CheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_date = request.checkDate or date.today()
    if check_date != date.today():
        raise AppException("每日打卡只能提交当天记录，历史日期请使用补卡")
    row = save_check_in(db, current_user.id, request, check_date, False)
    return ok(check_in_dict(row))


@router.post("/makeup")
def makeup(
    request: CheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.checkDate is None or request.checkDate >= date.today():
        raise AppException("补卡日期必须早于今天")
    row = save_check_in(db, current_user.id, request, request.checkDate, True)
    return ok(check_in_dict(row))
