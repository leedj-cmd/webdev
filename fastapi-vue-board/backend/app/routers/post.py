from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])

# 1. 목록 조회 + 검색 + 필터링 (GET)
@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = Query(None, description="제목 또는 내용 검색"),
    job_category: Optional[str] = Query(None, description="직무별 필터"),
    region: Optional[str] = Query(None, description="지역별 필터"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Post)

    # 검색어가 있으면 제목이나 내용에 포함된 것만 찾음 (ilike는 대소문자 무시)
    if search:
        query = query.where(Post.title.ilike(f"%{search}%") | Post.content.ilike(f"%{search}%"))
    
    # 직무 필터가 있으면 해당 직무만 찾음
    if job_category:
        query = query.where(Post.job_category == job_category)
        
    # 지역 필터가 있으면 해당 지역만 찾음
    if region:
        query = query.where(Post.region == region)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# 2. 상세 조회 (GET)
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

# 3. 게시글 작성 (POST)
@router.post("/", response_model=PostResponse)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db)):
    post = Post(**data.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

# 4. 게시글 수정 (PATCH)
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, data: PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 입력된 데이터만 업데이트
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    await db.commit()
    await db.refresh(post)
    return post

# 5. 게시글 삭제 (DELETE)
@router.delete("/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    await db.delete(post)
    await db.commit()
    return {"message": "게시글이 성공적으로 삭제되었습니다."}