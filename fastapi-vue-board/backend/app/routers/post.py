from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from sqlalchemy import update

from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.models.interaction import PostLike
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

# 1. 목록 조회 + 검색 + 필터링 (GET)
@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None),
    job_category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # 게시글별 좋아요 수 서브쿼리
    likes_subq = (
        select(PostLike.post_id, func.count(PostLike.user_id).label("like_count"))
        .group_by(PostLike.post_id)
        .subquery()
    )

    # Post + User(작성자명) + 좋아요 수 한 번에 조회
    query = (
        select(Post, User.username, likes_subq.c.like_count)
        .join(User, Post.author_id == User.id, isouter=True)
        .outerjoin(likes_subq, Post.id == likes_subq.c.post_id)
    )

    if search:
        query = query.where(Post.title.ilike(f"%{search}%") | Post.content.ilike(f"%{search}%"))
    if job_category:
        query = query.where(Post.job_category == job_category)
    if region:
        query = query.where(Post.region == region)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)

    posts = []
    for row in result.all():
        post, username, like_count = row
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "job_category": post.job_category,
            "region": post.region,
            "author_id": post.author_id,
            "author_name": username,
            "view_count": post.view_count,
            "like_count": like_count or 0,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }
        posts.append(post_dict)
    return posts


# 인기 게시글 조회 (조회수 기준)
@router.get("/popular", response_model=List[PostResponse])
async def get_popular_posts(db: AsyncSession = Depends(get_db)):
    query = select(Post).order_by(desc(Post.view_count)).limit(10)
    result = await db.execute(query)
    return result.scalars().all()


# 인기 게시글 조회 (좋아요 기준)
@router.get("/like_count", response_model=List[PostResponse])
async def get_like_posts(db: AsyncSession = Depends(get_db)):
    query = (
        select(Post, func.count(PostLike.post_id).label("like_count"))
        .outerjoin(PostLike, Post.id == PostLike.post_id)
        .group_by(Post.id)
        .order_by(desc("like_count"))
        .limit(10)
    )
    result = await db.execute(query)
    return [row[0] for row in result.all()]


# 2. 상세 조회 (GET)
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post, User.username)
        .join(User, Post.author_id == User.id, isouter=True)
        .where(Post.id == post_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    post, username = row
    post.author_name = username
    post.view_count += 1
    await db.commit()
    await db.refresh(post)
    return post


from app.services.ai_service import ai_service

# 3. 게시글 작성 (POST)
@router.post("/", response_model=PostResponse)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.is_suspended:
        raise HTTPException(status_code=403, detail="정지된 계정은 게시글을 작성할 수 없습니다.")

    # 비속어/공격성 체크
    censorship_result = ai_service.check_censorship(f"{data.title} {data.content}")
    if censorship_result['is_offensive']:
        raise HTTPException(
            status_code=400,
            detail=f"부적절한 표현이 감지되었습니다. (감지된 라벨: {censorship_result['label']})"
        )

    post_data = data.model_dump()
    post_data.pop('author_id', None)

    post = Post(**post_data, author_id=current_user.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


# 4. 게시글 수정 (PATCH)
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar()

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 게시글만 수정할 수 있습니다.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    await db.commit()
    await db.refresh(post)
    return post


# 5. 게시글 삭제 (DELETE)
@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar()

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="본인 게시글만 삭제할 수 있습니다.")

    await db.delete(post)
    await db.commit()
    return {"message": "게시글이 성공적으로 삭제되었습니다."}