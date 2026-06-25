from datetime import date, datetime

from sqlalchemy.orm import Session

from .models import Badge, CheckIn, Goal, UserBadge
from .schemas import goal_dict


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
