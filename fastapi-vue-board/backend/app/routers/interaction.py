from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.database import get_db
from app.models.interaction import PostLike, PostBookmark
from app.models.post import Post
from app.schemas.post import PostResponse
from app.models.user import User
from app.dependencies import get_current_user, get_optional_current_user
from app.routers.notification import create_notification

router = APIRouter(prefix="/interactions", tags=["Interactions"])


# ── 좋아요 수 + 현재 유저 좋아요 여부 조회
@router.get("/{post_id}/likes/status")
async def get_like_status(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    count_result = await db.execute(
        select(func.count(PostLike.user_id)).where(PostLike.post_id == post_id)
    )
    count = count_result.scalar() or 0

    is_liked = False
    if current_user:
        like_result = await db.execute(
            select(PostLike).where(
                PostLike.post_id == post_id,
                PostLike.user_id == current_user.id
            )
        )
        is_liked = like_result.scalar_one_or_none() is not None

    return {"count": count, "is_liked": is_liked}


# ── 좋아요 추가
@router.post("/{post_id}/likes")
async def add_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 좋아요를 누르셨습니다.")

    db.add(PostLike(post_id=post_id, user_id=current_user.id))
    await db.commit()

    # 알림: 게시글 작성자에게
    post = await db.get(Post, post_id)
    if post and post.author_id != current_user.id:
        await create_notification(
            db=db,
            recipient_id=post.author_id,
            actor_name=current_user.username,
            notification_type="post_like",
            message=f"{current_user.username}님이 좋아요를 눌렀습니다.",
            related_type="post",
            related_id=post_id,
        )

    return {"message": "좋아요가 추가되었습니다."}


# ── 좋아요 취소
@router.delete("/{post_id}/likes/{user_id}")
async def remove_like(post_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == user_id)
    result = await db.execute(query)
    like = result.scalar_one_or_none()

    if not like:
        raise HTTPException(status_code=404, detail="좋아요 기록이 없습니다.")

    await db.delete(like)
    await db.commit()
    return {"message": "좋아요가 취소되었습니다."}


# ── 북마크 추가
@router.post("/{post_id}/bookmarks")
async def add_bookmark(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(PostBookmark).where(PostBookmark.post_id == post_id, PostBookmark.user_id == current_user.id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 북마크하셨습니다.")

    db.add(PostBookmark(post_id=post_id, user_id=current_user.id))
    await db.commit()
    return {"message": "북마크가 추가되었습니다."}


# ── 북마크 취소
@router.delete("/{post_id}/bookmarks/{user_id}")
async def remove_bookmark(post_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PostBookmark).where(PostBookmark.post_id == post_id, PostBookmark.user_id == user_id)
    result = await db.execute(query)
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크 기록이 없습니다.")

    await db.delete(bookmark)
    await db.commit()
    return {"message": "북마크가 취소되었습니다."}


# 북마크 목록 조회
@router.get("/bookmarks", response_model=list[PostResponse])
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post)
        .join(PostBookmark, Post.id == PostBookmark.post_id)
        .where(PostBookmark.user_id == current_user.id)
        .order_by(PostBookmark.created_at.desc())
    )
    return result.scalars().all()