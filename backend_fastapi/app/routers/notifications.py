from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..common import AppException, ok
from ..deps import get_current_user, get_db
from ..models import CheckIn, Goal, Notification, User
from ..schemas import notification_dict

router = APIRouter(prefix="/api/notifications", tags=["消息提醒"])


def today_range():
    today = date.today()
    return (
        datetime.combine(today, time.min),
        datetime.combine(today, time.max),
    )


def goal_occurs_on_date(goal: Goal, target: date) -> bool:
    if target < goal.start_date or target > goal.end_date:
        return False
    day_diff = (target - goal.start_date).days
    if goal.cycle == "WEEKLY":
        return day_diff % 7 == 0
    if goal.cycle == "MONTHLY":
        return target.day == goal.start_date.day
    return True


def has_checkin(db: Session, user_id: int, goal_id: int, target: date) -> bool:
    return (
        db.query(CheckIn)
        .filter(
            CheckIn.user_id == user_id,
            CheckIn.goal_id == goal_id,
            CheckIn.check_date == target,
            CheckIn.status == "DONE",
        )
        .first()
        is not None
    )


def upsert_today_notification(db: Session, user_id: int, type_: str, title: str, content: str):
    start, end = today_range()
    exists = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.type == type_,
            Notification.title == title,
            Notification.create_time >= start,
            Notification.create_time <= end,
        )
        .first()
    )
    if exists is not None:
        if exists.content != content:
            exists.content = content
            exists.is_read = False
            exists.create_time = datetime.now()
        return
    db.add(
        Notification(
            user_id=user_id,
            type=type_,
            title=title,
            content=content,
            is_read=False,
            create_time=datetime.now(),
        )
    )


def active_goals_for_user(db: Session, user_id: int):
    today = date.today()
    return (
        db.query(Goal)
        .filter(
            Goal.user_id == user_id,
            Goal.status == "ACTIVE",
            Goal.start_date <= today,
            Goal.end_date >= today,
        )
        .order_by(Goal.end_date.asc(), Goal.id.asc())
        .all()
    )


def generate_daily_checkin_reminders(db: Session, user_id: int):
    today = date.today()
    pending = [
        goal for goal in active_goals_for_user(db, user_id)
        if goal_occurs_on_date(goal, today) and not has_checkin(db, user_id, goal.id, today)
    ]
    if not pending:
        return
    sample = "、".join(goal.name for goal in pending[:3])
    suffix = "" if len(pending) <= 3 else f"等 {len(pending)} 个目标"
    upsert_today_notification(
        db,
        user_id,
        "DAILY_CHECK_IN",
        "今日打卡提醒",
        f"你今天还有 {len(pending)} 个目标未打卡：{sample}{suffix}。记得按计划完成。",
    )


def generate_goal_expire_warnings(db: Session, user_id: int):
    today = date.today()
    warning_end = today + timedelta(days=3)
    goals = (
        db.query(Goal)
        .filter(
            Goal.user_id == user_id,
            Goal.status == "ACTIVE",
            Goal.end_date >= today,
            Goal.end_date <= warning_end,
        )
        .order_by(Goal.end_date.asc(), Goal.id.asc())
        .all()
    )
    for goal in goals:
        days_left = (goal.end_date - today).days
        day_text = "今天到期" if days_left == 0 else f"还剩 {days_left} 天"
        upsert_today_notification(
            db,
            user_id,
            "GOAL_EXPIRE",
            f"目标到期预警：{goal.name}",
            f"目标「{goal.name}」{day_text}，请及时完成剩余打卡或调整计划。",
        )


def generate_streak_break_reminders(db: Session, user_id: int):
    yesterday = date.today() - timedelta(days=1)
    goals = [
        goal for goal in active_goals_for_user(db, user_id)
        if goal_occurs_on_date(goal, yesterday) and not has_checkin(db, user_id, goal.id, yesterday)
    ]
    if not goals:
        return
    sample = "、".join(goal.name for goal in goals[:3])
    suffix = "" if len(goals) <= 3 else f"等 {len(goals)} 个目标"
    upsert_today_notification(
        db,
        user_id,
        "STREAK_BREAK",
        "连续打卡中断提醒",
        f"你昨天有 {len(goals)} 个计划未打卡：{sample}{suffix}。今天可以重新开始，避免持续中断。",
    )


def generate_smart_reminders(db: Session, user_id: int):
    generate_daily_checkin_reminders(db, user_id)
    generate_goal_expire_warnings(db, user_id)
    generate_streak_break_reminders(db, user_id)
    db.commit()


@router.post("/generate")
def generate_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    generate_smart_reminders(db, current_user.id)
    unread_count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )
    return ok({"unreadCount": unread_count})


@router.get("")
def list_notifications(
    unreadOnly: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    generate_smart_reminders(db, current_user.id)
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unreadOnly:
        query = query.filter(Notification.is_read == False)
    total = query.count()
    unread_count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )
    rows = (
        query.order_by(Notification.create_time.desc(), Notification.id.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )
    return ok({
        "list": [notification_dict(row) for row in rows],
        "page": page,
        "pageSize": pageSize,
        "total": total,
        "unreadCount": unread_count,
    })


@router.get("/unread-count")
def unread_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    generate_smart_reminders(db, current_user.id)
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )
    return ok({"unreadCount": count})


@router.put("/read-all")
def mark_all_notifications_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == current_user.id).update({"is_read": True})
    db.commit()
    return ok()


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if notification is None:
        raise AppException("消息不存在", 404)
    notification.is_read = True
    db.commit()
    return ok()


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if notification is None:
        raise AppException("消息不存在", 404)
    db.delete(notification)
    db.commit()
    return ok()
