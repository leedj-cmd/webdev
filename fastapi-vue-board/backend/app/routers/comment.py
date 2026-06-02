from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.dependencies import get_current_user
from app.routers.notification import create_notification

router = APIRouter(prefix="/comments", tags=["Comments"])


from app.services.ai_service import ai_service

# 1. 댓글 작성
@router.post("/posts/{post_id}", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.is_suspended:
        raise HTTPException(status_code=403, detail="정지된 계정은 댓글을 작성할 수 없습니다.")

    # 비속어/공격성 체크
    censorship_result = ai_service.check_censorship(comment.content)
    if censorship_result['is_offensive']:
        raise HTTPException(
            status_code=400, 
            detail=f"부적절한 표현이 감지되었습니다. (감지된 라벨: {censorship_result['label']})"
        )

    # 여기서 user_id는 로그인한 유저(current_user.id)를 사용합니다.
    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment.content,
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    # 알림 로직
    post = await db.get(Post, post_id)
    if post and post.author_id != current_user.id:
        await create_notification(
            db=db,
            recipient_id=post.author_id,
            actor_name=current_user.username,
            notification_type="post_comment",
            message=f"{current_user.username}님이 댓글을 작성하였습니다.",
            related_type="post",
            related_id=post_id,
        )

    if comment.parent_id:
        parent = await db.get(Comment, comment.parent_id)
        if parent and parent.user_id and parent.user_id != current_user.id:
            if not post or parent.user_id != post.author_id:
                await create_notification(
                    db=db,
                    recipient_id=parent.user_id,
                    actor_name=current_user.username,
                    notification_type="post_comment",
                    message=f"{current_user.username}님이 대댓글을 작성하였습니다.",
                    related_type="post",
                    related_id=post_id,
                )

    return new_comment


# 2. 특정 게시글의 전체 댓글 조회
@router.get("/posts/{post_id}", response_model=List[CommentResponse])
async def get_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
    )
    return result.scalars().all()


# 3. 댓글 수정
@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    target_comment = result.scalar_one_or_none()
    
    if not target_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if target_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 댓글만 수정할 수 있습니다.")

    # 비속어/공격성 체크
    censorship_result = ai_service.check_censorship(comment_update.content)
    if censorship_result['is_offensive']:
        raise HTTPException(
            status_code=400, 
            detail=f"부적절한 표현이 감지되었습니다. (감지된 라벨: {censorship_result['label']})"
        )

    target_comment.content = comment_update.content
    await db.commit()
    await db.refresh(target_comment)
    return target_comment


# 4. 댓글 삭제
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    target_comment = result.scalar_one_or_none()
    
    if not target_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if target_comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="본인 댓글만 삭제할 수 있습니다.")

    await db.delete(target_comment)
    await db.commit()
    return None