from datetime import date, datetime

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    email: str | None = None


class ProfileRequest(BaseModel):
    username: str = Field(min_length=1)
    email: str | None = None


class PasswordRequest(BaseModel):
    oldPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=1)


class GoalRequest(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    startDate: date
    endDate: date
    cycle: str = Field(min_length=1)
    dailyTargetCount: int = Field(ge=1)
    status: str | None = None


class CheckInRequest(BaseModel):
    goalId: int
    checkDate: date | None = None
    remark: str | None = None


def user_profile(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "createTime": user.create_time,
    }


def goal_dict(goal):
    return {
        "id": goal.id,
        "userId": goal.user_id,
        "name": goal.name,
        "type": goal.type,
        "startDate": goal.start_date,
        "endDate": goal.end_date,
        "cycle": goal.cycle,
        "dailyTargetCount": goal.daily_target_count,
        "status": goal.status,
        "createTime": goal.create_time,
        "updateTime": goal.update_time,
    }


def check_in_dict(row):
    return {
        "id": row.id,
        "goalId": row.goal_id,
        "userId": row.user_id,
        "checkDate": row.check_date,
        "checkTime": row.check_time,
        "status": row.status,
        "remark": row.remark,
        "makeup": row.makeup,
    }


def badge_dict(badge, obtained_time: datetime | None = None):
    data = {
        "id": badge.id,
        "code": badge.code,
        "name": badge.name,
        "description": badge.description,
        "conditionText": badge.condition_text,
    }
    if obtained_time is not None:
        data["obtainedTime"] = obtained_time
    return data
