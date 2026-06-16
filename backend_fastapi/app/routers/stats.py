from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..business import completed_count, current_streak_days, goal_progress
from ..common import ok
from ..deps import get_current_user, get_db
from ..models import CheckIn, Goal, User

router = APIRouter(prefix="/api/stats", tags=["统计"])


def shift_month(base: date, delta: int) -> date:
    month_index = base.year * 12 + base.month - 1 + delta
    year = month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def monthly_report(db: Session, user_id: int):
    rows = db.query(CheckIn).filter(CheckIn.user_id == user_id, CheckIn.status == "DONE").all()
    grouped = {}
    for row in rows:
        month = row.check_date.strftime("%Y-%m")
        grouped[month] = grouped.get(month, 0) + 1
    start = shift_month(date.today().replace(day=1), -5)
    result = []
    for index in range(6):
        month = shift_month(start, index).strftime("%Y-%m")
        result.append({"month": month, "count": grouped.get(month, 0)})
    return result


@router.get("/dashboard")
def dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_goals = db.query(Goal).filter(Goal.user_id == current_user.id).count()
    active_goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id, Goal.status == "ACTIVE")
        .count()
    )
    total_check_ins = completed_count(db, current_user.id)
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    progress = [goal_progress(db, current_user.id, goal) for goal in goals]
    average_rate = 0 if not progress else sum(item["completionRate"] for item in progress) / len(progress)
    return ok(
        {
            "totalGoals": total_goals,
            "activeGoals": active_goals,
            "totalCheckIns": total_check_ins,
            "currentStreakDays": current_streak_days(db, current_user.id),
            "averageCompletionRate": round(average_rate, 1),
            "monthlyReport": monthly_report(db, current_user.id),
            "goalProgress": progress,
        }
    )
