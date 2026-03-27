from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import os

from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# 1. 게시글 작성 
@router.post("/", response_model=PostResponse)
async def create_post(
    post: PostCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # strip()은 양끝의 공백(스페이스바, 엔터)을 모두 지워주는 함수
    if not post.title or not post.title.strip():
        raise HTTPException(status_code=400, detail="제목을 반드시 입력해야 합니다.")
        
    if not post.content or not post.content.strip():
        raise HTTPException(status_code=400, detail="내용을 반드시 입력해야 합니다.")

    new_post = Post(**post.model_dump(), author_id=current_user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post

# 2. 게시글 목록 보기 + 제목 검색
@router.get("/", response_model=List[PostResponse])
async def get_posts(
    search: Optional[str] = None, 
    skip: int = 0,                
    limit: int = 10,              
    db: AsyncSession = Depends(get_db)
):
    query = select(Post)
    
    if search:
        query = query.where(Post.title.contains(search))
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    return posts

# 3. 게시글 상세 보기 + 조회수 증가
@router.get("/{post_id}", response_model=PostResponse)
async def get_post_detail(post_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
    post.view_count += 1
    await db.commit()
    await db.refresh(post)
    return post

# 4. 게시글 수정 (파일 변경은 제외, 텍스트만 수정)
@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int, 
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    if post_update.title is not None and not post_update.title.strip():
        raise HTTPException(status_code=400, detail="수정할 제목이 비어있을 수 없습니다.")
    if post_update.content is not None and not post_update.content.strip():
        raise HTTPException(status_code=400, detail="수정할 내용이 비어있을 수 없습니다.")

    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="글을 수정할 권한이 없습니다.")
        
    update_data = post_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)
        
    await db.commit()
    await db.refresh(post)
    return post

# 5. 게시글 삭제(첨부파일도 함께 삭제)
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="글을 삭제할 권한이 없습니다.")
        
    # 첨부파일이 존재하면 서버 디스크에서도 삭제
    if post.file_url:
        file_path = os.path.join(".", post.file_url.lstrip("/"))
        if os.path.exists(file_path):
            os.remove(file_path)

    await db.delete(post)
    await db.commit()
    return None