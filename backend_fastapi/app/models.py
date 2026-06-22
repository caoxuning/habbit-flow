from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120))
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class Goal(Base):
    __tablename__ = "goal"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[object] = mapped_column(Date, nullable=False)
    end_date: Mapped[object] = mapped_column(Date, nullable=False)
    cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    daily_target_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)
    update_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class CheckIn(Base):
    __tablename__ = "check_in"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    goal_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("goal.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    check_date: Mapped[object] = mapped_column(Date, nullable=False)
    check_time: Mapped[object] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DONE")
    remark: Mapped[str | None] = mapped_column(String(500))
    makeup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Badge(Base):
    __tablename__ = "badge"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    condition_text: Mapped[str] = mapped_column(String(255), nullable=False)


class UserBadge(Base):
    __tablename__ = "user_badge"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    badge_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("badge.id"), nullable=False)
    obtained_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class Friendship(Base):
    __tablename__ = "friendship"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    requester_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    addressee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    message: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)
    update_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class SocialCircle(Base):
    __tablename__ = "social_circle"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(20), nullable=False, default="TAG")
    owner_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class CircleMember(Base):
    __tablename__ = "circle_member"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    circle_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("social_circle.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="MEMBER")
    join_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class CirclePost(Base):
    __tablename__ = "circle_post"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    circle_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("social_circle.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class PostLike(Base):
    __tablename__ = "post_like"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("circle_post.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)


class PostComment(Base):
    __tablename__ = "post_comment"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("circle_post.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    create_time: Mapped[object] = mapped_column(DateTime, nullable=False)
