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
