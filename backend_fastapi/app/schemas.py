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
    priority: str | None = None
    status: str | None = None


class CheckInRequest(BaseModel):
    goalId: int
    checkDate: date | None = None
    remark: str | None = None


class FriendRequest(BaseModel):
    targetUserId: int
    message: str | None = None


class CircleRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    icon: str | None = None


class CirclePostRequest(BaseModel):
    content: str = Field(min_length=1)
    visibility: str | None = None


class PostCommentRequest(BaseModel):
    content: str = Field(min_length=1)


class DirectMessageRequest(BaseModel):
    content: str = Field(min_length=1)


class CheckInShareRequest(BaseModel):
    checkInId: int
    content: str = Field(min_length=1)
    visibility: str = "PUBLIC"
    circleId: int | None = None
    shareToFriends: bool = True
    friendIds: list[int] | None = None


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
        "priority": goal.priority,
        "status": goal.status,
        "createTime": goal.create_time,
        "updateTime": goal.update_time,
    }


def check_in_dict(row, goal=None):
    data = {
        "id": row.id,
        "goalId": row.goal_id,
        "userId": row.user_id,
        "checkDate": row.check_date,
        "checkTime": row.check_time,
        "status": row.status,
        "remark": row.remark,
        "makeup": row.makeup,
    }
    if goal is not None:
        data["goalName"] = goal.name
        data["goalType"] = goal.type
    return data


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


def notification_dict(notification):
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "content": notification.content,
        "read": notification.is_read,
        "createTime": notification.create_time,
    }


def user_summary(user, friendship_status: str | None = None):
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    if friendship_status is not None:
        data["friendshipStatus"] = friendship_status
    return data


def friendship_dict(friendship, requester, receiver):
    return {
        "id": friendship.id,
        "requester": user_summary(requester),
        "receiver": user_summary(receiver),
        "message": friendship.message,
        "status": friendship.status,
        "createTime": friendship.create_time,
        "updateTime": friendship.update_time,
    }


def friend_view(user, friendship):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "friendshipId": friendship.id,
        "friendSince": friendship.update_time,
    }


def circle_dict(circle, owner=None, joined: bool = False):
    return {
        "id": circle.id,
        "name": circle.name,
        "description": circle.description,
        "icon": circle.icon,
        "ownerId": circle.owner_user_id,
        "ownerName": owner.username if owner is not None else None,
        "memberCount": circle.member_count,
        "joined": joined,
        "createTime": circle.create_time,
    }


def circle_member_dict(member, user):
    return {
        "userId": user.id,
        "username": user.username,
        "email": user.email,
        "role": member.role,
        "joinTime": member.join_time,
    }


def circle_post_dict(post, circle, author, like_count: int = 0, comment_count: int = 0, liked: bool = False):
    return {
        "id": post.id,
        "circleId": circle.id,
        "circleName": circle.name,
        "author": user_summary(author),
        "checkInId": post.check_in_id,
        "visibility": post.visibility,
        "postType": post.post_type,
        "content": post.content,
        "likeCount": like_count,
        "commentCount": comment_count,
        "liked": liked,
        "createTime": post.create_time,
    }


def post_comment_dict(comment, author):
    return {
        "id": comment.id,
        "postId": comment.post_id,
        "author": user_summary(author),
        "content": comment.content,
        "createTime": comment.create_time,
    }


def direct_message_dict(message, sender, receiver):
    return {
        "id": message.id,
        "sender": user_summary(sender),
        "receiver": user_summary(receiver),
        "content": message.content,
        "createTime": message.create_time,
    }
