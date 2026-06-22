from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..common import AppException, ok
from ..deps import get_current_user, get_db
from ..models import CircleMember, CirclePost, DirectMessage, Friendship, PostComment, PostLike, SocialCircle, User
from ..schemas import (
    CirclePostRequest,
    CircleRequest,
    DirectMessageRequest,
    FriendRequest,
    PostCommentRequest,
    circle_dict,
    circle_member_dict,
    circle_post_dict,
    direct_message_dict,
    friend_view,
    friendship_dict,
    post_comment_dict,
    user_summary,
)

router = APIRouter(prefix="/api/social", tags=["社交"])


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


def serialize_post(db: Session, post: CirclePost, current_user_id: int):
    circle = db.query(SocialCircle).filter(SocialCircle.id == post.circle_id).first()
    author = db.query(User).filter(User.id == post.user_id).first()
    like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
    comment_count = db.query(PostComment).filter(PostComment.post_id == post.id).count()
    liked = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user_id)
        .first()
        is not None
    )
    return circle_post_dict(post, circle, author, like_count, comment_count, liked)


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
    return ok([serialize_post(db, row, current_user.id) for row in rows])


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
        content=request.content,
        create_time=datetime.now(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return ok(serialize_post(db, post, current_user.id))


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    require_circle_member(db, post.circle_id, current_user.id)
    exists = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
    )
    if exists is None:
        db.add(PostLike(post_id=post.id, user_id=current_user.id, create_time=datetime.now()))
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
    require_circle_member(db, post.circle_id, current_user.id)
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
    require_circle_member(db, post.circle_id, current_user.id)
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
    require_circle_member(db, post.circle_id, current_user.id)
    comment = PostComment(
        post_id=post.id,
        user_id=current_user.id,
        content=request.content,
        create_time=datetime.now(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return ok(post_comment_dict(comment, current_user))


@router.get("/feed")
def feed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(CircleMember.circle_id).filter(CircleMember.user_id == current_user.id).all()
    circle_ids = [row[0] for row in memberships]
    if not circle_ids:
        return ok([])
    rows = (
        db.query(CirclePost)
        .filter(CirclePost.circle_id.in_(circle_ids))
        .order_by(CirclePost.create_time.desc())
        .limit(50)
        .all()
    )
    return ok([serialize_post(db, row, current_user.id) for row in rows])
