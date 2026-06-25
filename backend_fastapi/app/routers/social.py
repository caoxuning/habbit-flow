from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

from ..common import AppException, ok
from ..deps import get_current_user, get_db
from ..models import CheckIn, CircleMember, CirclePost, DirectMessage, Friendship, Goal, PostComment, PostLike, SocialCircle, User
from ..schemas import (
    CheckInShareRequest,
    CirclePostRequest,
    CircleRequest,
    DirectMessageRequest,
    FriendRequest,
    PostCommentRequest,
    circle_dict,
    circle_member_dict,
    circle_post_dict,
    check_in_dict,
    direct_message_dict,
    friend_view,
    friendship_dict,
    post_comment_dict,
    user_summary,
)

router = APIRouter(prefix="/api/social", tags=["社交"])
POST_VISIBILITIES = {"PUBLIC", "FRIENDS", "CIRCLE", "PRIVATE"}


def normalize_visibility(value: str | None) -> str:
    visibility = (value or "PUBLIC").upper()
    if visibility not in POST_VISIBILITIES:
        raise AppException("动态可见范围不正确")
    return visibility


def friendship_between(db: Session, left_user_id: int, right_user_id: int) -> Friendship | None:
    return (
        db.query(Friendship)
        .filter(
            or_(
                (Friendship.requester_id == left_user_id) & (Friendship.addressee_id == right_user_id),
                (Friendship.requester_id == right_user_id) & (Friendship.addressee_id == left_user_id),
            )
        )
        .order_by(Friendship.update_time.desc())
        .first()
    )


def friendship_status(db: Session, current_user_id: int, target_user_id: int) -> str:
    friendship = friendship_between(db, current_user_id, target_user_id)
    return "NONE" if friendship is None else friendship.status


def require_friendship(db: Session, current_user_id: int, target_user_id: int):
    friendship = friendship_between(db, current_user_id, target_user_id)
    if friendship is None or friendship.status != "ACCEPTED":
        raise AppException("成为好友后才能聊天")


def friend_ids_for_user(db: Session, user_id: int) -> list[int]:
    rows = (
        db.query(Friendship)
        .filter(
            Friendship.status == "ACCEPTED",
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
        )
        .all()
    )
    return [row.addressee_id if row.requester_id == user_id else row.requester_id for row in rows]


def get_circle(db: Session, circle_id: int) -> SocialCircle:
    circle = db.query(SocialCircle).filter(SocialCircle.id == circle_id).first()
    if circle is None:
        raise AppException("圈子不存在", 404)
    return circle


def get_member(db: Session, circle_id: int, user_id: int) -> CircleMember | None:
    return (
        db.query(CircleMember)
        .filter(CircleMember.circle_id == circle_id, CircleMember.user_id == user_id)
        .first()
    )


def serialize_circle(db: Session, circle: SocialCircle, current_user_id: int):
    owner = None
    if circle.owner_user_id is not None:
        owner = db.query(User).filter(User.id == circle.owner_user_id).first()
    joined = get_member(db, circle.id, current_user_id) is not None
    return circle_dict(circle, owner, joined)


def get_post(db: Session, post_id: int) -> CirclePost:
    post = db.query(CirclePost).filter(CirclePost.id == post_id).first()
    if post is None:
        raise AppException("帖子不存在", 404)
    return post


def require_circle_member(db: Session, circle_id: int, user_id: int):
    if get_member(db, circle_id, user_id) is None:
        raise AppException("加入圈子后才能操作")


def can_view_post(db: Session, post: CirclePost, current_user_id: int) -> bool:
    if post.user_id == current_user_id:
        return True
    if post.visibility == "PRIVATE":
        return False
    if post.visibility == "FRIENDS":
        friendship = friendship_between(db, current_user_id, post.user_id)
        return friendship is not None and friendship.status == "ACCEPTED"
    if post.visibility == "CIRCLE":
        return get_member(db, post.circle_id, current_user_id) is not None
    return True


def serialize_post(db: Session, post: CirclePost, current_user_id: int):
    circle = db.query(SocialCircle).filter(SocialCircle.id == post.circle_id).first()
    author = db.query(User).filter(User.id == post.user_id).first()
    check_in = None
    goal = None
    if post.check_in_id is not None:
        row = (
            db.query(CheckIn, Goal)
            .join(Goal, CheckIn.goal_id == Goal.id)
            .filter(CheckIn.id == post.check_in_id)
            .first()
        )
        if row is not None:
            check_in, goal = row
    like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
    comment_count = db.query(PostComment).filter(PostComment.post_id == post.id).count()
    liked = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user_id)
        .first()
        is not None
    )
    return circle_post_dict(post, circle, author, like_count, comment_count, liked, check_in, goal)


def notify_friends_for_checkin(
    db: Session,
    sender: User,
    friend_ids: list[int],
    goal: Goal,
    post: CirclePost | None,
):
    if not friend_ids:
        return
    now = datetime.now()
    content = f"{sender.username} 完成了「{goal.name}」打卡"
    if post is not None:
        content += "，并分享了一条打卡动态，快去鼓励一下吧。"
    else:
        content += "，快去鼓励一下吧。"
    for friend_id in friend_ids:
        db.add(DirectMessage(
            sender_id=sender.id,
            receiver_id=friend_id,
            content=content,
            create_time=now,
        ))


@router.get("/users/search")
def search_users(
    keyword: str = Query(min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .filter(User.id != current_user.id, User.username.like(f"%{keyword}%"))
        .order_by(User.create_time.desc())
        .limit(20)
        .all()
    )
    return ok([user_summary(user, friendship_status(db, current_user.id, user.id)) for user in users])


@router.post("/friend-requests")
def request_friend(
    request: FriendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.targetUserId == current_user.id:
        raise AppException("不能添加自己为好友")
    target = db.query(User).filter(User.id == request.targetUserId).first()
    if target is None:
        raise AppException("目标用户不存在", 404)
    existing = friendship_between(db, current_user.id, target.id)
    if existing is not None and existing.status in ("PENDING", "ACCEPTED"):
        raise AppException("已存在好友关系或待处理申请")
    now = datetime.now()
    if existing is not None and existing.status == "REJECTED":
        existing.requester_id = current_user.id
        existing.addressee_id = target.id
        existing.message = request.message
        existing.status = "PENDING"
        existing.update_time = now
        friendship = existing
    else:
        friendship = Friendship(
            requester_id=current_user.id,
            addressee_id=target.id,
            message=request.message,
            status="PENDING",
            create_time=now,
            update_time=now,
        )
        db.add(friendship)
    db.commit()
    db.refresh(friendship)
    return ok(friendship_dict(friendship, current_user, target))


@router.get("/friend-requests")
def list_friend_requests(
    type: str = Query(default="received"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Friendship)
    if type == "sent":
        query = query.filter(Friendship.requester_id == current_user.id)
    else:
        query = query.filter(Friendship.addressee_id == current_user.id)
    rows = query.order_by(Friendship.create_time.desc()).all()
    result = []
    for row in rows:
        requester = db.query(User).filter(User.id == row.requester_id).first()
        receiver = db.query(User).filter(User.id == row.addressee_id).first()
        result.append(friendship_dict(row, requester, receiver))
    return ok(result)


@router.put("/friend-requests/{request_id}/accept")
def accept_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friendship = (
        db.query(Friendship)
        .filter(Friendship.id == request_id, Friendship.addressee_id == current_user.id)
        .first()
    )
    if friendship is None:
        raise AppException("好友申请不存在", 404)
    if friendship.status != "PENDING":
        raise AppException("该好友申请已处理")
    friendship.status = "ACCEPTED"
    friendship.update_time = datetime.now()
    db.commit()
    return ok()


@router.put("/friend-requests/{request_id}/reject")
def reject_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friendship = (
        db.query(Friendship)
        .filter(Friendship.id == request_id, Friendship.addressee_id == current_user.id)
        .first()
    )
    if friendship is None:
        raise AppException("好友申请不存在", 404)
    if friendship.status != "PENDING":
        raise AppException("该好友申请已处理")
    friendship.status = "REJECTED"
    friendship.update_time = datetime.now()
    db.commit()
    return ok()


@router.get("/friends")
def list_friends(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Friendship)
        .filter(
            Friendship.status == "ACCEPTED",
            or_(Friendship.requester_id == current_user.id, Friendship.addressee_id == current_user.id),
        )
        .order_by(Friendship.update_time.desc())
        .all()
    )
    result = []
    for row in rows:
        friend_id = row.addressee_id if row.requester_id == current_user.id else row.requester_id
        friend = db.query(User).filter(User.id == friend_id).first()
        result.append(friend_view(friend, row))
    return ok(result)


@router.get("/friends/checkins/today")
def friends_today_checkins(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friend_ids = friend_ids_for_user(db, current_user.id)
    if not friend_ids:
        return ok([])
    today = date.today()
    result = []
    for friend in db.query(User).filter(User.id.in_(friend_ids)).order_by(User.username.asc()).all():
        active_goal_count = (
            db.query(Goal)
            .filter(
                Goal.user_id == friend.id,
                Goal.status == "ACTIVE",
                Goal.start_date <= today,
                Goal.end_date >= today,
            )
            .count()
        )
        rows = (
            db.query(CheckIn, Goal)
            .join(Goal, CheckIn.goal_id == Goal.id)
            .filter(CheckIn.user_id == friend.id, CheckIn.check_date == today)
            .order_by(CheckIn.check_time.desc())
            .all()
        )
        result.append({
            "friend": user_summary(friend),
            "activeGoalCount": active_goal_count,
            "doneCount": len(rows),
            "checkedIn": len(rows) > 0,
            "latestCheckIn": check_in_dict(rows[0][0], rows[0][1]) if rows else None,
        })
    return ok(result)


@router.get("/leaderboards")
def social_leaderboards(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend_ids = friend_ids_for_user(db, current_user.id)
    scoped_user_ids = [current_user.id, *friend_ids]
    user_checkin_count = func.count(CheckIn.id)
    friend_rows = (
        db.query(User, user_checkin_count.label("check_in_count"))
        .outerjoin(CheckIn, CheckIn.user_id == User.id)
        .filter(User.id.in_(scoped_user_ids))
        .group_by(User.id, User.username, User.email, User.create_time)
        .order_by(user_checkin_count.desc(), User.username.asc())
        .limit(limit)
        .all()
    )
    friend_leaderboard = [
        {
            "rank": index + 1,
            "user": user_summary(user),
            "checkInCount": int(check_in_count or 0),
            "isMe": user.id == current_user.id,
        }
        for index, (user, check_in_count) in enumerate(friend_rows)
    ]

    circle_checkin_count = func.count(func.distinct(case((CircleMember.id.isnot(None), CheckIn.id))))
    circle_rows = (
        db.query(SocialCircle, circle_checkin_count.label("check_in_count"))
        .outerjoin(
            CirclePost,
            and_(
                CirclePost.circle_id == SocialCircle.id,
                CirclePost.post_type == "CHECK_IN",
                CirclePost.check_in_id.isnot(None),
            ),
        )
        .outerjoin(CheckIn, CheckIn.id == CirclePost.check_in_id)
        .outerjoin(
            CircleMember,
            and_(
                CircleMember.circle_id == SocialCircle.id,
                CircleMember.user_id == CirclePost.user_id,
                CheckIn.check_time >= CircleMember.join_time,
            ),
        )
        .group_by(
            SocialCircle.id,
            SocialCircle.name,
            SocialCircle.description,
            SocialCircle.icon,
            SocialCircle.owner_user_id,
            SocialCircle.member_count,
            SocialCircle.create_time,
        )
        .order_by(circle_checkin_count.desc(), SocialCircle.member_count.desc(), SocialCircle.name.asc())
        .limit(limit)
        .all()
    )
    circle_leaderboard = [
        {
            "rank": index + 1,
            "circle": serialize_circle(db, circle, current_user.id),
            "checkInCount": int(check_in_count or 0),
        }
        for index, (circle, check_in_count) in enumerate(circle_rows)
    ]
    return ok({
        "friends": friend_leaderboard,
        "circles": circle_leaderboard,
    })


@router.get("/friends/{friend_id}/messages")
def list_direct_messages(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend = db.query(User).filter(User.id == friend_id).first()
    if friend is None:
        raise AppException("好友不存在", 404)
    require_friendship(db, current_user.id, friend.id)
    rows = (
        db.query(DirectMessage)
        .filter(
            or_(
                (DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == friend.id),
                (DirectMessage.sender_id == friend.id) & (DirectMessage.receiver_id == current_user.id),
            )
        )
        .order_by(DirectMessage.create_time.asc(), DirectMessage.id.asc())
        .limit(100)
        .all()
    )
    result = []
    user_map = {current_user.id: current_user, friend.id: friend}
    for row in rows:
        result.append(direct_message_dict(row, user_map[row.sender_id], user_map[row.receiver_id]))
    return ok(result)


@router.post("/friends/{friend_id}/messages")
def send_direct_message(
    friend_id: int,
    request: DirectMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend = db.query(User).filter(User.id == friend_id).first()
    if friend is None:
        raise AppException("好友不存在", 404)
    require_friendship(db, current_user.id, friend.id)
    message = DirectMessage(
        sender_id=current_user.id,
        receiver_id=friend.id,
        content=request.content.strip(),
        create_time=datetime.now(),
    )
    if not message.content:
        raise AppException("消息内容不能为空")
    db.add(message)
    db.commit()
    db.refresh(message)
    return ok(direct_message_dict(message, current_user, friend))


@router.get("/circles")
def list_circles(
    keyword: str | None = None,
    joined: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SocialCircle)
    if keyword:
        query = query.filter(SocialCircle.name.like(f"%{keyword}%"))
    circles = query.order_by(SocialCircle.create_time.desc()).all()
    result = [serialize_circle(db, circle, current_user.id) for circle in circles]
    if joined is not None:
        result = [item for item in result if item["joined"] == joined]
    return ok(result)


@router.post("/circles")
def create_circle(
    request: CircleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.query(SocialCircle).filter(SocialCircle.name == request.name).first()
    if exists is not None:
        raise AppException("圈子名称已存在")
    now = datetime.now()
    circle = SocialCircle(
        name=request.name,
        description=request.description,
        icon=request.icon or "TAG",
        owner_user_id=current_user.id,
        member_count=1,
        create_time=now,
    )
    db.add(circle)
    db.flush()
    db.add(CircleMember(circle_id=circle.id, user_id=current_user.id, role="OWNER", join_time=now))
    db.commit()
    db.refresh(circle)
    return ok(serialize_circle(db, circle, current_user.id))


@router.get("/circles/{circle_id}")
def circle_detail(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    circle = get_circle(db, circle_id)
    return ok(serialize_circle(db, circle, current_user.id))


@router.post("/circles/{circle_id}/join")
def join_circle(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    circle = get_circle(db, circle_id)
    if get_member(db, circle.id, current_user.id) is not None:
        raise AppException("已加入该圈子")
    db.add(CircleMember(circle_id=circle.id, user_id=current_user.id, role="MEMBER", join_time=datetime.now()))
    circle.member_count += 1
    db.commit()
    return ok()


@router.delete("/circles/{circle_id}/leave")
def leave_circle(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    circle = get_circle(db, circle_id)
    if circle.owner_user_id == current_user.id:
        raise AppException("圈主不能直接退出自己创建的圈子")
    member = get_member(db, circle.id, current_user.id)
    if member is None:
        raise AppException("尚未加入该圈子")
    db.delete(member)
    circle.member_count = max(0, circle.member_count - 1)
    db.commit()
    return ok()


@router.get("/circles/{circle_id}/members")
def list_circle_members(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_circle(db, circle_id)
    rows = (
        db.query(CircleMember)
        .filter(CircleMember.circle_id == circle_id)
        .order_by(CircleMember.join_time.asc())
        .all()
    )
    result = []
    for row in rows:
        user = db.query(User).filter(User.id == row.user_id).first()
        result.append(circle_member_dict(row, user))
    return ok(result)


@router.get("/circles/{circle_id}/posts")
def list_circle_posts(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_circle(db, circle_id)
    rows = (
        db.query(CirclePost)
        .filter(CirclePost.circle_id == circle_id)
        .order_by(CirclePost.create_time.desc())
        .limit(50)
        .all()
    )
    return ok([serialize_post(db, row, current_user.id) for row in rows if can_view_post(db, row, current_user.id)])


@router.post("/circles/{circle_id}/posts")
def publish_post(
    circle_id: int,
    request: CirclePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    circle = get_circle(db, circle_id)
    if get_member(db, circle.id, current_user.id) is None:
        raise AppException("加入圈子后才能发帖")
    post = CirclePost(
        circle_id=circle.id,
        user_id=current_user.id,
        visibility=normalize_visibility(request.visibility),
        post_type="NORMAL",
        content=request.content,
        create_time=datetime.now(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return ok(serialize_post(db, post, current_user.id))


@router.post("/checkins/share")
def share_check_in(
    request: CheckInShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(CheckIn, Goal)
        .join(Goal, CheckIn.goal_id == Goal.id)
        .filter(CheckIn.id == request.checkInId, CheckIn.user_id == current_user.id)
        .first()
    )
    if row is None:
        raise AppException("打卡记录不存在", 404)
    checkin, goal = row
    visibility = normalize_visibility(request.visibility)
    post = None
    if visibility != "PRIVATE":
        circle_id = request.circleId
        if circle_id is None:
            membership = (
                db.query(CircleMember)
                .filter(CircleMember.user_id == current_user.id)
                .order_by(CircleMember.join_time.asc())
                .first()
            )
            if membership is None:
                raise AppException("请先加入一个圈子，或选择仅通知好友/仅自己可见")
            circle_id = membership.circle_id
        circle = get_circle(db, circle_id)
        membership = get_member(db, circle.id, current_user.id)
        if membership is None:
            raise AppException("加入圈子后才能分享动态")
        if checkin.check_time < membership.join_time:
            raise AppException("只能分享加入该圈子之后产生的打卡")
        post = CirclePost(
            circle_id=circle.id,
            user_id=current_user.id,
            check_in_id=checkin.id,
            visibility=visibility,
            post_type="CHECK_IN",
            content=request.content.strip(),
            create_time=datetime.now(),
        )
        db.add(post)

    notified_ids: list[int] = []
    if request.shareToFriends:
        available_friend_ids = set(friend_ids_for_user(db, current_user.id))
        requested_friend_ids = request.friendIds or list(available_friend_ids)
        notified_ids = [friend_id for friend_id in requested_friend_ids if friend_id in available_friend_ids]
        notify_friends_for_checkin(db, current_user, notified_ids, goal, post)

    db.commit()
    if post is not None:
        db.refresh(post)
    return ok({
        "post": serialize_post(db, post, current_user.id) if post is not None else None,
        "notifiedFriendCount": len(notified_ids),
    })


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not can_view_post(db, post, current_user.id):
        raise AppException("无权查看该动态", 403)
    exists = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
    )
    if exists is None:
        db.add(PostLike(post_id=post.id, user_id=current_user.id, create_time=datetime.now()))
        if post.user_id != current_user.id:
            db.add(DirectMessage(
                sender_id=current_user.id,
                receiver_id=post.user_id,
                content=f"{current_user.username} 给你的打卡动态点了赞。",
                create_time=datetime.now(),
            ))
        db.commit()
    like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
    return ok({"liked": True, "likeCount": like_count})


@router.delete("/posts/{post_id}/like")
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not can_view_post(db, post, current_user.id):
        raise AppException("无权查看该动态", 403)
    exists = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
    )
    if exists is not None:
        db.delete(exists)
        db.commit()
    like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
    return ok({"liked": False, "likeCount": like_count})


@router.get("/posts/{post_id}/comments")
def list_post_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not can_view_post(db, post, current_user.id):
        raise AppException("无权查看该动态", 403)
    rows = (
        db.query(PostComment)
        .filter(PostComment.post_id == post.id)
        .order_by(PostComment.create_time.asc())
        .all()
    )
    result = []
    for row in rows:
        author = db.query(User).filter(User.id == row.user_id).first()
        result.append(post_comment_dict(row, author))
    return ok(result)


@router.post("/posts/{post_id}/comments")
def create_post_comment(
    post_id: int,
    request: PostCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not can_view_post(db, post, current_user.id):
        raise AppException("无权查看该动态", 403)
    comment = PostComment(
        post_id=post.id,
        user_id=current_user.id,
        content=request.content,
        create_time=datetime.now(),
    )
    db.add(comment)
    if post.user_id != current_user.id:
        db.add(DirectMessage(
            sender_id=current_user.id,
            receiver_id=post.user_id,
            content=f"{current_user.username} 评论了你的打卡动态：{request.content}",
            create_time=datetime.now(),
        ))
    db.commit()
    db.refresh(comment)
    return ok(post_comment_dict(comment, current_user))


@router.get("/feed")
def feed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(CircleMember.circle_id).filter(CircleMember.user_id == current_user.id).all()
    circle_ids = [row[0] for row in memberships]
    friend_ids = friend_ids_for_user(db, current_user.id)
    rows = (
        db.query(CirclePost)
        .filter(
            or_(
                CirclePost.user_id == current_user.id,
                CirclePost.circle_id.in_(circle_ids or [-1]),
                CirclePost.user_id.in_(friend_ids or [-1]),
            )
        )
        .order_by(CirclePost.create_time.desc())
        .limit(50)
        .all()
    )
    return ok([serialize_post(db, row, current_user.id) for row in rows if can_view_post(db, row, current_user.id)])
