from datetime import date, datetime

from sqlalchemy.orm import Session

from .models import Badge, CheckIn, Goal, SocialCircle, UserBadge
from .schemas import goal_dict


BADGE_SEEDS = [
    ("FIRST_CHECK_IN", "初次打卡勋章", "完成第一次目标打卡，开启自律记录。", "累计完成打卡 1 次"),
    ("STREAK_7", "连续7天勋章", "连续坚持一周，形成稳定节奏。", "连续打卡 7 天"),
    ("STREAK_30", "连续30天勋章", "连续坚持一个月，习惯已经成型。", "连续打卡 30 天"),
    ("CHECK_IN_100", "百次打卡勋章", "累计完成一百次打卡，长期执行力突出。", "累计完成打卡 100 次"),
    ("DISCIPLINE_MASTER", "自律达人勋章", "兼具长期积累和连续坚持的综合奖励。", "累计 100 次且连续 30 天"),
]

CIRCLE_SEEDS = [
    ("英语打卡圈", "记录背单词、口语练习、阅读训练，和同伴一起保持输入输出。", "EN"),
    ("健身打卡圈", "分享训练计划、跑步记录和饮食控制，让运动习惯更稳定。", "FIT"),
    ("阅读打卡圈", "沉淀每日阅读页数、读书笔记和阶段复盘。", "READ"),
]


def seed_badges(db: Session):
    for code, name, description, condition_text in BADGE_SEEDS:
        exists = db.query(Badge).filter(Badge.code == code).first()
        if exists is None:
            db.add(Badge(code=code, name=name, description=description, condition_text=condition_text))
    db.commit()


def seed_circles(db: Session):
    for name, description, icon in CIRCLE_SEEDS:
        exists = db.query(SocialCircle).filter(SocialCircle.name == name).first()
        if exists is None:
            db.add(
                SocialCircle(
                    name=name,
                    description=description,
                    icon=icon,
                    owner_user_id=None,
                    member_count=0,
                    create_time=datetime.now(),
                )
            )
    db.commit()


def expected_count(goal: Goal, today: date | None = None) -> int:
    if goal.end_date < goal.start_date:
        return 0
    days = (goal.end_date - goal.start_date).days + 1
    if goal.cycle == "WEEKLY":
        count = 0
        current = goal.start_date
        while current <= goal.end_date:
            if current.weekday() == 0:
                count += 1
            current = current.fromordinal(current.toordinal() + 1)
        occurrences = max(1, count)
    elif goal.cycle == "MONTHLY":
        occurrences = (goal.end_date.year - goal.start_date.year) * 12 + goal.end_date.month - goal.start_date.month + 1
    else:
        occurrences = days
    return occurrences * goal.daily_target_count


def completed_count(db: Session, user_id: int, goal_id: int | None = None) -> int:
    query = db.query(CheckIn).filter(CheckIn.user_id == user_id, CheckIn.status == "DONE")
    if goal_id is not None:
        query = query.filter(CheckIn.goal_id == goal_id)
    return query.count()


def current_streak_days(db: Session, user_id: int) -> int:
    rows = db.query(CheckIn.check_date).filter(CheckIn.user_id == user_id, CheckIn.status == "DONE").all()
    dates = {row[0] for row in rows}
    streak = 0
    current = date.today()
    while current in dates:
        streak += 1
        current = current.fromordinal(current.toordinal() - 1)
    return streak


def goal_progress(db: Session, user_id: int, goal: Goal) -> dict:
    completed = completed_count(db, user_id, goal.id)
    expected = expected_count(goal)
    completion_rate = 0 if expected == 0 else min(100, completed * 100 / expected)
    return {
        "goal": goal_dict(goal),
        "completedCount": completed,
        "expectedCount": expected,
        "completionRate": round(completion_rate, 1),
        "currentStreakDays": current_streak_days(db, user_id),
    }


def grant_badge_if(db: Session, user_id: int, code: str, matched: bool):
    if not matched:
        return
    badge = db.query(Badge).filter(Badge.code == code).first()
    if badge is None:
        return
    exists = db.query(UserBadge).filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge.id).first()
    if exists is None:
        db.add(UserBadge(user_id=user_id, badge_id=badge.id, obtained_time=datetime.now()))


def evaluate_and_grant_badges(db: Session, user_id: int):
    total = completed_count(db, user_id)
    streak = current_streak_days(db, user_id)
    grant_badge_if(db, user_id, "FIRST_CHECK_IN", total >= 1)
    grant_badge_if(db, user_id, "STREAK_7", streak >= 7)
    grant_badge_if(db, user_id, "STREAK_30", streak >= 30)
    grant_badge_if(db, user_id, "CHECK_IN_100", total >= 100)
    grant_badge_if(db, user_id, "DISCIPLINE_MASTER", total >= 100 and streak >= 30)
