from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from typing import List, Optional

from app.database import get_db
from app.models.community import Community, CommunityComment
from app.models.community_like import CommunityLike, CommunityCommentLike
from app.models.user import User
from app.schemas.community import (
    CommunityCreate, CommunityUpdate, CommunityRead,
    CommunityCommentCreate, CommunityCommentUpdate, CommunityCommentRead,
)
from app.dependencies import get_current_user, get_optional_current_user
from app.routers.notification import create_notification

router = APIRouter(prefix="/community", tags=["Community"])

# 카테고리 유효값 (영어 키)
VALID_CATEGORIES = {"job", "career", "project"}


def _build_community_dict(community: Community, username: Optional[str], like_count: int, comment_count: int) -> dict:
    return {
        "id": community.id,
        "title": community.title,
        "content": community.content,
        "category": community.category,
        "is_anonymous": community.is_anonymous,
        "owner_id": community.owner_id,                              # 익명이어도 소유권 판단용으로 항상 반환
        "author_name": None if community.is_anonymous else username,  # 표시 이름만 익명 처리
        "created_at": community.created_at,
        "updated_at": community.updated_at,
        "like_count": like_count,
        "comment_count": comment_count,
    }


# ── 1. 목록 조회 (카테고리 필터 / 전체)
@router.get("/", response_model=List[CommunityRead])
async def get_communities(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    likes_subq = (
        select(CommunityLike.community_id, func.count(CommunityLike.user_id).label("like_count"))
        .group_by(CommunityLike.community_id)
        .subquery()
    )
    comments_subq = (
        select(CommunityComment.community_id, func.count(CommunityComment.id).label("comment_count"))
        .where(CommunityComment.parent_id == None)
        .group_by(CommunityComment.community_id)
        .subquery()
    )

    query = (
        select(Community, User.username, likes_subq.c.like_count, comments_subq.c.comment_count)
        .join(User, Community.owner_id == User.id, isouter=True)
        .outerjoin(likes_subq, Community.id == likes_subq.c.community_id)
        .outerjoin(comments_subq, Community.id == comments_subq.c.community_id)
        .order_by(Community.created_at.desc())
    )
    if category and category in VALID_CATEGORIES:
        query = query.where(Community.category == category)

    result = await db.execute(query)
    rows = result.all()

    return [
        _build_community_dict(c, username, like_count or 0, comment_count or 0)
        for c, username, like_count, comment_count in rows
    ]


# ── 2. 단건 조회
@router.get("/{community_id}", response_model=CommunityRead)
async def get_community(community_id: int, db: AsyncSession = Depends(get_db)):
    likes_subq = (
        select(CommunityLike.community_id, func.count(CommunityLike.user_id).label("like_count"))
        .group_by(CommunityLike.community_id)
        .subquery()
    )
    comments_subq = (
        select(CommunityComment.community_id, func.count(CommunityComment.id).label("comment_count"))
        .where(CommunityComment.parent_id == None)
        .group_by(CommunityComment.community_id)
        .subquery()
    )

    result = await db.execute(
        select(Community, User.username, likes_subq.c.like_count, comments_subq.c.comment_count)
        .join(User, Community.owner_id == User.id, isouter=True)
        .outerjoin(likes_subq, Community.id == likes_subq.c.community_id)
        .outerjoin(comments_subq, Community.id == comments_subq.c.community_id)
        .where(Community.id == community_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    c, username, like_count, comment_count = row
    return _build_community_dict(c, username, like_count or 0, comment_count or 0)


# ── 3. 게시글 작성 (로그인 필요)
@router.post("/", response_model=CommunityRead)
async def create_community(
    req: CommunityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 카테고리입니다. ({', '.join(VALID_CATEGORIES)})")

    new_post = Community(
        title=req.title,
        content=req.content,
        category=req.category,
        is_anonymous=req.is_anonymous,
        owner_id=current_user.id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return _build_community_dict(
        new_post,
        None if req.is_anonymous else current_user.username,
        0, 0,
    )


# ── 4. 게시글 수정 (작성자 본인만)
@router.patch("/{community_id}", response_model=CommunityRead)
async def update_community(
    community_id: int,
    req: CommunityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 게시글만 수정할 수 있습니다.")
    if req.category and req.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="유효하지 않은 카테고리입니다.")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post)

    # 좋아요/댓글 수 다시 조회
    like_count_res = await db.execute(
        select(func.count(CommunityLike.user_id)).where(CommunityLike.community_id == community_id)
    )
    comment_count_res = await db.execute(
        select(func.count(CommunityComment.id)).where(
            CommunityComment.community_id == community_id,
            CommunityComment.parent_id == None,
        )
    )
    return _build_community_dict(
        post,
        None if post.is_anonymous else current_user.username,
        like_count_res.scalar() or 0,
        comment_count_res.scalar() or 0,
    )


# ── 5. 게시글 삭제 (작성자 또는 관리자)
@router.delete("/{community_id}")
async def delete_community(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="본인 게시글만 삭제할 수 있습니다.")

    await db.delete(post)
    await db.commit()
    return {"message": "게시글이 삭제되었습니다."}


# ── 6. 좋아요 토글 (로그인 필요)
@router.post("/{community_id}/like")
async def toggle_community_like(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    result = await db.execute(
        select(CommunityLike).where(
            CommunityLike.community_id == community_id,
            CommunityLike.user_id == current_user.id,
        )
    )
    existing = result.scalars().first()

    if existing:
        await db.delete(existing)
        await db.commit()
        return {"message": "좋아요가 취소되었습니다.", "is_liked": False}

    db.add(CommunityLike(community_id=community_id, user_id=current_user.id))
    await db.commit()

    if community.owner_id and community.owner_id != current_user.id:
        display = "익명" if community.is_anonymous else current_user.username
        await create_notification(
            db=db,
            recipient_id=community.owner_id,
            actor_name=None if community.is_anonymous else current_user.username,
            notification_type="community_like",
            message=f"{display}님이 좋아요를 눌렀습니다.",
            related_type="community",
            related_id=community_id,
        )
    return {"message": "좋아요를 눌렀습니다.", "is_liked": True}


# ── 7. 좋아요 상태 조회
@router.get("/{community_id}/like/status")
async def get_like_status(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    count_res = await db.execute(
        select(func.count(CommunityLike.user_id)).where(CommunityLike.community_id == community_id)
    )
    count = count_res.scalar() or 0

    is_liked = False
    if current_user:
        like_res = await db.execute(
            select(CommunityLike).where(
                CommunityLike.community_id == community_id,
                CommunityLike.user_id == current_user.id,
            )
        )
        is_liked = like_res.scalar_one_or_none() is not None

    return {"count": count, "is_liked": is_liked}


# ── 8. 댓글 목록 조회
@router.get("/{community_id}/comments", response_model=List[CommunityCommentRead])
async def get_comments(community_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CommunityComment)
        .where(
            CommunityComment.community_id == community_id,
            CommunityComment.parent_id == None,
        )
        .order_by(CommunityComment.created_at.asc())
    )
    comments = result.scalars().all()

    out = []
    for c in comments:
        user_res = await db.execute(select(User).where(User.id == c.user_id)) if c.user_id else None
        user = user_res.scalar_one_or_none() if user_res else None
        like_res = await db.execute(
            select(func.count(CommunityCommentLike.user_id)).where(CommunityCommentLike.comment_id == c.id)
        )
        out.append({
            "id": c.id,
            "community_id": c.community_id,
            "user_id": c.user_id,                                              # 익명이어도 소유권 판단용으로 항상 반환
            "author_name": None if c.is_anonymous else (user.username if user else None),  # 표시 이름만 익명 처리
            "content": c.content,
            "is_anonymous": c.is_anonymous,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "like_count": like_res.scalar() or 0,
            "replies": [],
        })
    return out


# ── 9. 댓글 작성 (로그인 필요)
@router.post("/{community_id}/comments", response_model=CommunityCommentRead)
async def create_comment(
    community_id: int,
    req: CommunityCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    community = await db.get(Community, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    parent = None
    if req.parent_id:
        parent = await db.get(CommunityComment, req.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="부모 댓글을 찾을 수 없습니다.")

    new_comment = CommunityComment(
        community_id=community_id,
        user_id=current_user.id,        # 익명이어도 DB에는 항상 실제 user_id 저장
        content=req.content,
        is_anonymous=req.is_anonymous,
        parent_id=req.parent_id,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    if community.owner_id and community.owner_id != current_user.id:
        display = "익명" if req.is_anonymous else current_user.username
        await create_notification(
            db=db,
            recipient_id=community.owner_id,
            actor_name=None if req.is_anonymous else current_user.username,
            notification_type="community_comment",
            message=f"{display}님이 댓글을 작성하였습니다.",
            related_type="community",
            related_id=community_id,
        )

    return {
        "id": new_comment.id,
        "community_id": new_comment.community_id,
        "user_id": current_user.id,                                        # 항상 실제 user_id 반환
        "author_name": None if req.is_anonymous else current_user.username,
        "content": new_comment.content,
        "is_anonymous": new_comment.is_anonymous,
        "parent_id": new_comment.parent_id,
        "created_at": new_comment.created_at,
        "updated_at": new_comment.updated_at,
        "like_count": 0,
        "replies": [],
    }


# ── 10. 댓글 수정 (작성자 본인만)
@router.patch("/{community_id}/comments/{comment_id}", response_model=CommunityCommentRead)
async def update_comment(
    community_id: int,
    comment_id: int,
    req: CommunityCommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CommunityComment).where(CommunityComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 댓글만 수정할 수 있습니다.")

    comment.content = req.content
    await db.commit()
    await db.refresh(comment)

    like_res = await db.execute(
        select(func.count(CommunityCommentLike.user_id)).where(CommunityCommentLike.comment_id == comment_id)
    )
    return {
        "id": comment.id,
        "community_id": comment.community_id,
        "user_id": comment.user_id,                                        # 항상 실제 user_id 반환
        "author_name": None if comment.is_anonymous else current_user.username,
        "content": comment.content,
        "is_anonymous": comment.is_anonymous,
        "parent_id": comment.parent_id,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "like_count": like_res.scalar() or 0,
        "replies": [],
    }


# ── 11. 댓글 삭제 (작성자 또는 관리자)
@router.delete("/{community_id}/comments/{comment_id}")
async def delete_comment(
    community_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CommunityComment).where(CommunityComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="본인 댓글만 삭제할 수 있습니다.")

    await db.delete(comment)
    await db.commit()
    return {"message": "댓글이 삭제되었습니다."}
