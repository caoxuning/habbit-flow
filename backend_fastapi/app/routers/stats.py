from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..business import completed_count, current_streak_days, goal_progress
from ..common import ok
from ..deps import get_current_user, get_db
from ..models import CheckIn, Goal, User, UserBadge, Badge

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
    total_goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id, Goal.status != "ARCHIVED")
        .count()
    )
    active_goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id, Goal.status == "ACTIVE")
        .count()
    )
    total_check_ins = completed_count(db, current_user.id)
    goals = db.query(Goal).filter(Goal.user_id == current_user.id, Goal.status != "ARCHIVED").all()
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


@router.get("/timeline")
def growth_timeline(
    days: int = Query(default=30, ge=0, le=3650),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """成长日志时间线：按日期倒序展示打卡记录、获得勋章、每日推荐"""
    start_date = None if days == 0 else date.today() - timedelta(days=days - 1)

    # 1. 查询打卡记录
    checkins_query = (
        db.query(CheckIn, Goal.name, Goal.type)
        .join(Goal, CheckIn.goal_id == Goal.id)
        .filter(
            CheckIn.user_id == current_user.id,
            CheckIn.status == "DONE",
        )
        .order_by(CheckIn.check_date.desc(), CheckIn.check_time.desc())
    )
    if start_date is not None:
        checkins_query = checkins_query.filter(CheckIn.check_date >= start_date)
    checkins = checkins_query.all()

    # 2. 查询获得的勋章
    badges_query = (
        db.query(UserBadge, Badge.name, Badge.description)
        .join(Badge, UserBadge.badge_id == Badge.id)
        .filter(
            UserBadge.user_id == current_user.id,
        )
        .order_by(UserBadge.obtained_time.desc())
    )
    if start_date is not None:
        badges_query = badges_query.filter(UserBadge.obtained_time >= start_date)
    badges_obtained = badges_query.all()

    # 3. 按日期合并数据
    timeline = {}
    all_dates = set()

    for checkin, goal_name, goal_type in checkins:
        d = checkin.check_date.isoformat()
        all_dates.add(d)
        if d not in timeline:
            timeline[d] = {"date": d, "events": []}
        timeline[d]["events"].append({
            "type": "checkin",
            "goalName": goal_name,
            "goalType": goal_type,
            "remark": checkin.remark,
            "makeup": checkin.makeup,
            "time": checkin.check_time.isoformat(),
        })

    for ub, badge_name, badge_desc in badges_obtained:
        d = ub.obtained_time.strftime("%Y-%m-%d")
        if d not in timeline:
            timeline[d] = {"date": d, "events": []}
            all_dates.add(d)
        timeline[d]["events"].append({
            "type": "badge",
            "badgeName": badge_name,
            "badgeDescription": badge_desc,
        })

    # 4. 按日期倒序排列
    sorted_dates = sorted(timeline.keys(), reverse=True)
    return ok([timeline[d] for d in sorted_dates])
