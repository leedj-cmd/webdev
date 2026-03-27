from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])

# 1. 댓글 작성 (원본 댓글 & 대댓글 모두 이 API 하나로 처리합니다)
@router.post("/posts/{post_id}", response_model=CommentResponse)
async def create_comment(post_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    new_comment = Comment(
        post_id=post_id,
        user_id=comment.user_id,
        content=comment.content,
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

# 2. 특정 게시글의 전체 댓글 조회
@router.get("/posts/{post_id}", response_model=List[CommentResponse])
async def get_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    # 작성 시간순으로 정렬해서 가져옵니다
    result = await db.execute(select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at))
    return result.scalars().all()

# 3. 댓글 수정
@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_update: CommentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    target_comment = result.scalar_one_or_none()
    
    if not target_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    target_comment.content = comment_update.content
    await db.commit()
    await db.refresh(target_comment)
    return target_comment

# 4. 댓글 삭제
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    target_comment = result.scalar_one_or_none()
    
    if not target_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    await db.delete(target_comment)
    await db.commit()