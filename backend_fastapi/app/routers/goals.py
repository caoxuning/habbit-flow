from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..business import goal_progress
from ..common import AppException, ok
from ..deps import get_current_user, get_db
from ..models import Goal, Notification, User
from ..schemas import GoalRequest, goal_dict

router = APIRouter(prefix="/api/goals", tags=["目标"])


def owned_goal(db: Session, user_id: int, goal_id: int) -> Goal:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if goal is None:
        raise AppException("目标不存在", 404)
    return goal


def fill_goal(goal: Goal, request: GoalRequest):
    goal.name = request.name
    goal.type = request.type
    goal.start_date = request.startDate
    goal.end_date = request.endDate
    goal.cycle = request.cycle
    goal.daily_target_count = request.dailyTargetCount
    goal.priority = request.priority or "NORMAL"


@router.get("")
def list_goals(
    includeArchived: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Goal).filter(Goal.user_id == current_user.id)
    if not includeArchived:
        query = query.filter(Goal.status != "ARCHIVED")
    goals = (
        query
        .order_by(Goal.create_time.desc())
        .all()
    )
    return ok([goal_progress(db, current_user.id, goal) for goal in goals])


@router.post("")
def create_goal(
    request: GoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.endDate < request.startDate:
        raise AppException("结束日期不能早于开始日期")
    goal = Goal(user_id=current_user.id, status=request.status or "ACTIVE")
    fill_goal(goal, request)
    goal.create_time = datetime.now()
    goal.update_time = datetime.now()
    db.add(goal)
    db.flush()
    db.add(Notification(
        user_id=current_user.id,
        type="DAILY_CHECK_IN",
        title="新目标已创建",
        content=f"你已创建目标「{goal.name}」，记得按照计划完成每日打卡。",
        is_read=False,
        create_time=datetime.now(),
    ))
    db.commit()
    db.refresh(goal)
    return ok(goal_dict(goal))


@router.put("/{goal_id}")
def update_goal(
    goal_id: int,
    request: GoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.endDate < request.startDate:
        raise AppException("结束日期不能早于开始日期")
    goal = owned_goal(db, current_user.id, goal_id)
    fill_goal(goal, request)
    goal.status = request.status or goal.status
    goal.update_time = datetime.now()
    db.commit()
    db.refresh(goal)
    return ok(goal_dict(goal))


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = owned_goal(db, current_user.id, goal_id)
    goal.status = "ARCHIVED"
    goal.update_time = datetime.now()
    db.commit()
    return ok()
