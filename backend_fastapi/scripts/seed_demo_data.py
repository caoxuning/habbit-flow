import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.business import evaluate_and_grant_badges, seed_badges, seed_circles
from app.database import Base, SessionLocal, engine
from app.models import (
    CheckIn,
    CircleMember,
    CirclePost,
    Friendship,
    Goal,
    PostComment,
    PostLike,
    SocialCircle,
    User,
    UserBadge,
)
from app.security import hash_password


DEMO_PASSWORD = "123456"
DEMO_USERS = [
    ("demo_admin", "demo_admin@habitflow.local"),
    ("member1", "member1@habitflow.local"),
    ("member2", "member2@habitflow.local"),
    ("member3", "member3@habitflow.local"),
]
DEMO_CIRCLES = ["运动打卡圈", "英语打卡圈"]
RESET_CIRCLE_NAMES = [*DEMO_CIRCLES, "课设冲刺圈", "早起自律圈"]


def current_time():
    return datetime.now()


def fallback_ids(ids):
    return ids if ids else [0]


def ensure_user(db, username: str, email: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        user = User(username=username, password=hash_password(DEMO_PASSWORD), email=email, create_time=current_time())
        db.add(user)
        db.flush()
    else:
        user.email = email
        user.password = hash_password(DEMO_PASSWORD)
    return user


def ensure_goal(
    db,
    user: User,
    name: str,
    goal_type: str,
    days_before: int,
    days_after: int,
    priority: str = "NORMAL",
) -> Goal:
    goal = db.query(Goal).filter(Goal.user_id == user.id, Goal.name == name).first()
    today = date.today()
    start_date = today - timedelta(days=days_before)
    end_date = today + timedelta(days=days_after)
    if goal is None:
        goal = Goal(
            user_id=user.id,
            name=name,
            type=goal_type,
            start_date=start_date,
            end_date=end_date,
            cycle="DAILY",
            daily_target_count=1,
            priority=priority,
            status="ACTIVE",
            create_time=current_time(),
            update_time=current_time(),
        )
        db.add(goal)
        db.flush()
    goal.start_date = start_date
    goal.end_date = end_date
    goal.cycle = "DAILY"
    goal.daily_target_count = 1
    goal.priority = priority
    goal.status = "ACTIVE"
    goal.update_time = current_time()
    return goal


def ensure_check_in(db, user: User, goal: Goal, days_ago: int, remark: str):
    check_date = date.today() - timedelta(days=days_ago)
    exists = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user.id, CheckIn.goal_id == goal.id, CheckIn.check_date == check_date)
        .first()
    )
    if exists is not None:
        exists.remark = remark
        return exists
    row = CheckIn(
        user_id=user.id,
        goal_id=goal.id,
        check_date=check_date,
        check_time=current_time() - timedelta(days=days_ago),
        status="DONE",
        remark=remark,
        makeup=days_ago > 0,
    )
    db.add(row)
    return row


def ensure_friendship(db, requester: User, addressee: User, status: str, message: str):
    existing = (
        db.query(Friendship)
        .filter(
            ((Friendship.requester_id == requester.id) & (Friendship.addressee_id == addressee.id))
            | ((Friendship.requester_id == addressee.id) & (Friendship.addressee_id == requester.id))
        )
        .first()
    )
    if existing is None:
        existing = Friendship(
            requester_id=requester.id,
            addressee_id=addressee.id,
            create_time=current_time(),
            update_time=current_time(),
        )
        db.add(existing)
    existing.status = status
    existing.message = message
    existing.update_time = current_time()
    return existing


def ensure_circle(db, name: str, description: str, icon: str, owner: User) -> SocialCircle:
    circle = db.query(SocialCircle).filter(SocialCircle.name == name).first()
    if circle is None:
        circle = SocialCircle(
            name=name,
            description=description,
            icon=icon,
            owner_user_id=owner.id,
            member_count=0,
            create_time=current_time(),
        )
        db.add(circle)
        db.flush()
    circle.description = description
    circle.icon = icon
    circle.owner_user_id = owner.id
    return circle


def ensure_member(db, circle: SocialCircle, user: User, role: str = "MEMBER"):
    member = (
        db.query(CircleMember)
        .filter(CircleMember.circle_id == circle.id, CircleMember.user_id == user.id)
        .first()
    )
    if member is None:
        member = CircleMember(circle_id=circle.id, user_id=user.id, join_time=current_time())
        db.add(member)
    member.role = role
    return member


def ensure_post(db, circle: SocialCircle, author: User, content: str, minutes_ago: int) -> CirclePost:
    post = (
        db.query(CirclePost)
        .filter(CirclePost.circle_id == circle.id, CirclePost.user_id == author.id, CirclePost.content == content)
        .first()
    )
    if post is None:
        post = CirclePost(
            circle_id=circle.id,
            user_id=author.id,
            content=content,
            create_time=current_time() - timedelta(minutes=minutes_ago),
        )
        db.add(post)
        db.flush()
    return post


def ensure_like(db, post: CirclePost, user: User):
    exists = db.query(PostLike).filter(PostLike.post_id == post.id, PostLike.user_id == user.id).first()
    if exists is None:
        db.add(PostLike(post_id=post.id, user_id=user.id, create_time=current_time()))


def ensure_comment(db, post: CirclePost, user: User, content: str):
    exists = (
        db.query(PostComment)
        .filter(PostComment.post_id == post.id, PostComment.user_id == user.id, PostComment.content == content)
        .first()
    )
    if exists is None:
        db.add(PostComment(post_id=post.id, user_id=user.id, content=content, create_time=current_time()))


def reset_demo(db):
    users = db.query(User).filter(User.username.in_([username for username, _ in DEMO_USERS])).all()
    user_ids = [user.id for user in users]
    circle_ids = [
        row[0]
        for row in db.query(SocialCircle.id)
        .filter((SocialCircle.name.in_(RESET_CIRCLE_NAMES)) | (SocialCircle.owner_user_id.in_(fallback_ids(user_ids))))
        .all()
    ]
    post_ids = [
        row[0]
        for row in db.query(CirclePost.id)
        .filter((CirclePost.user_id.in_(fallback_ids(user_ids))) | (CirclePost.circle_id.in_(fallback_ids(circle_ids))))
        .all()
    ]

    db.query(PostComment).filter(
        (PostComment.user_id.in_(fallback_ids(user_ids))) | (PostComment.post_id.in_(fallback_ids(post_ids)))
    ).delete(synchronize_session=False)
    db.query(PostLike).filter(
        (PostLike.user_id.in_(fallback_ids(user_ids))) | (PostLike.post_id.in_(fallback_ids(post_ids)))
    ).delete(synchronize_session=False)
    db.query(CirclePost).filter(CirclePost.id.in_(fallback_ids(post_ids))).delete(synchronize_session=False)
    db.query(CircleMember).filter(
        (CircleMember.user_id.in_(fallback_ids(user_ids))) | (CircleMember.circle_id.in_(fallback_ids(circle_ids)))
    ).delete(synchronize_session=False)
    db.query(SocialCircle).filter(SocialCircle.id.in_(fallback_ids(circle_ids))).delete(synchronize_session=False)
    db.query(Friendship).filter(
        (Friendship.requester_id.in_(fallback_ids(user_ids)))
        | (Friendship.addressee_id.in_(fallback_ids(user_ids)))
    ).delete(synchronize_session=False)
    db.query(UserBadge).filter(UserBadge.user_id.in_(fallback_ids(user_ids))).delete(synchronize_session=False)
    db.query(CheckIn).filter(CheckIn.user_id.in_(fallback_ids(user_ids))).delete(synchronize_session=False)
    db.query(Goal).filter(Goal.user_id.in_(fallback_ids(user_ids))).delete(synchronize_session=False)
    db.query(User).filter(User.id.in_(fallback_ids(user_ids))).delete(synchronize_session=False)
    db.commit()


def seed_demo(db):
    users = {username: ensure_user(db, username, email) for username, email in DEMO_USERS}
    db.flush()

    goals = {
        "demo_admin": [
            ensure_goal(db, users["demo_admin"], "每天背 30 个单词", "STUDY", 35, 30, "IMPORTANT"),
            ensure_goal(db, users["demo_admin"], "晚间拉伸 15 分钟", "SPORT", 20, 40, "NORMAL"),
        ],
        "member1": [
            ensure_goal(db, users["member1"], "早起 7 点前起床", "LIFE", 28, 30, "NORMAL"),
            ensure_goal(db, users["member1"], "跑步 3 公里", "SPORT", 18, 30, "IMPORTANT"),
        ],
        "member2": [
            ensure_goal(db, users["member2"], "阅读专业书 20 页", "READING", 25, 30, "IMPORTANT"),
        ],
        "member3": [
            ensure_goal(db, users["member3"], "力量训练 45 分钟", "SPORT", 30, 30, "URGENT"),
            ensure_goal(db, users["member3"], "英语听力精听 20 分钟", "STUDY", 12, 30, "IMPORTANT"),
        ],
    }

    remarks = ["按计划完成", "今天状态不错", "补上昨天记录", "有点累但坚持了", "继续保持节奏"]
    for username, user_goals in goals.items():
        streak_days = {"demo_admin": 12, "member1": 6, "member2": 9, "member3": 15}[username]
        for index in range(streak_days):
            ensure_check_in(db, users[username], user_goals[0], index, remarks[index % len(remarks)])
        if len(user_goals) > 1:
            for index in (0, 2, 4, 7, 10):
                ensure_check_in(db, users[username], user_goals[1], index, "完成今日训练安排")

    ensure_friendship(db, users["member3"], users["demo_admin"], "ACCEPTED", "一起坚持运动和英语打卡")
    ensure_friendship(db, users["member3"], users["member1"], "ACCEPTED", "互相监督打卡")
    ensure_friendship(db, users["member2"], users["member3"], "PENDING", "一起交流阅读和英语学习")

    sport = ensure_circle(db, "运动打卡圈", "记录跑步、力量训练和拉伸恢复，和同伴一起保持运动节奏。", "FIT", users["member3"])
    english = ensure_circle(db, "英语打卡圈", "分享背单词、听力精听和口语练习，稳定积累英语输入输出。", "EN", users["demo_admin"])
    for circle in (sport, english):
        for user in users.values():
            role = "OWNER" if user.id == circle.owner_user_id else "MEMBER"
            ensure_member(db, circle, user, role)

    posts = [
        ensure_post(db, sport, users["member3"], "今天完成 45 分钟力量训练，深蹲和卧推都比上周稳定一些。", 40),
        ensure_post(db, english, users["demo_admin"], "今天背完 30 个新单词，晚上准备再听一遍 BBC 慢速英语。", 85),
        ensure_post(db, sport, users["member1"], "早起跑步 3 公里完成，配速比昨天快了一点。", 130),
    ]
    ensure_like(db, posts[0], users["demo_admin"])
    ensure_like(db, posts[0], users["member1"])
    ensure_like(db, posts[1], users["member3"])
    ensure_comment(db, posts[0], users["demo_admin"], "很稳，训练后记得拉伸一下，明天腿部可能会酸。")
    ensure_comment(db, posts[0], users["member2"], "这个训练量可以，我今天也准备补一组核心训练。")
    ensure_comment(db, posts[1], users["member3"], "我也在练听力，精听完再跟读效果会更好。")

    for circle in (sport, english):
        circle.member_count = db.query(CircleMember).filter(CircleMember.circle_id == circle.id).count()

    db.flush()
    for user in users.values():
        evaluate_and_grant_badges(db, user.id)
    db.commit()
    return users


def main():
    parser = argparse.ArgumentParser(description="Seed HabitFlow demo data.")
    parser.add_argument("--reset-demo", action="store_true", help="delete seeded demo accounts and recreate them")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_badges(db)
        seed_circles(db)
        if args.reset_demo:
            reset_demo(db)
        users = seed_demo(db)
        print("Demo data is ready.")
        print("Accounts:")
        for username in users:
            print(f"  {username} / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
