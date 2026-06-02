# filename: backend/app/routers/contest.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.database import get_db
from app.models.contest import Contest
from app.models.scrap import Scrap
from app.schemas.contest import ContestCreate, ContestUpdate, ContestResponse
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.external_opportunities import fetch_external_contests

router = APIRouter(prefix="/contests", tags=["Contests"])

def require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")

# 1. 공모전 목록 + 검색 + 필터
@router.get("/", response_model=List[ContestResponse])
async def get_contests(
    skip: int = 0,
    limit: int = 10,
    include_external: bool = True,
    external_limit: int = 30,
    search: Optional[str] = Query(None, description="제목/주최측/키워드 검색"),
    category: Optional[str] = Query(None),
    target: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Contest).where(Contest.is_active == True)

    if search:
        query = query.where(
            or_(
                Contest.title.ilike(f"%{search}%"),
                Contest.organizer.ilike(f"%{search}%"),
                Contest.description.ilike(f"%{search}%"),
                Contest.category.ilike(f"%{search}%")
            )
        )
    if category:
        query = query.where(Contest.category == category)
    if target:
        query = query.where(Contest.target == target)

    query = query.order_by(Contest.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    contests = list(result.scalars().all())

    if not include_external:
        return contests

    external_contests = await fetch_external_contests(limit=min(max(external_limit, 0), 50))
    if search:
        lowered = search.lower()
        external_contests = [
            contest for contest in external_contests
            if any(lowered in str(contest.get(field) or "").lower() for field in ["title", "organizer", "description", "category"])
        ]
    if category:
        external_contests = [
            contest for contest in external_contests
            if category in (contest.get("category") or "") or category in (contest.get("description") or "")
        ]
    if target:
        external_contests = [
            contest for contest in external_contests
            if target in (contest.get("target") or "")
        ]

    return contests + external_contests

# 2. 공모전 상세 조회
@router.get("/{contest_id}", response_model=ContestResponse)
async def get_contest(contest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="공모전을 찾을 수 없습니다.")
    return contest

# 3. 공모전 등록 (관리자만)
@router.post("/", response_model=ContestResponse, status_code=201)
async def create_contest(
    data: ContestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    new_contest = Contest(**data.model_dump(), author_id=current_user.id)
    db.add(new_contest)
    await db.commit()
    await db.refresh(new_contest)
    return new_contest

# 4. 공모전 수정 (관리자만)
@router.patch("/{contest_id}", response_model=ContestResponse)
async def update_contest(
    contest_id: int,
    data: ContestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="공모전을 찾을 수 없습니다.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contest, key, value)

    await db.commit()
    await db.refresh(contest)
    return contest

# 5. 공모전 삭제 (관리자만) - 소프트 삭제
@router.delete("/{contest_id}")
async def delete_contest(
    contest_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="공모전을 찾을 수 없습니다.")

    contest.is_active = False
    await db.commit()
    return {"message": "공모전이 비활성화되었습니다."}

# 6. 스크랩 추가
@router.post("/{contest_id}/scrap")
async def scrap_contest(
    contest_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Scrap).where(
        Scrap.contest_id == contest_id, Scrap.user_id == current_user.id
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 스크랩한 공모전입니다.")

    new_scrap = Scrap(user_id=current_user.id, contest_id=contest_id, scrap_type="contest")
    db.add(new_scrap)
    await db.commit()
    return {"message": "스크랩되었습니다."}

# 7. 스크랩 취소
@router.delete("/{contest_id}/scrap")
async def unscrap_contest(
    contest_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Scrap).where(
        Scrap.contest_id == contest_id, Scrap.user_id == current_user.id
    )
    result = await db.execute(query)
    scrap = result.scalar_one_or_none()
    if not scrap:
        raise HTTPException(status_code=404, detail="스크랩 기록이 없습니다.")

    await db.delete(scrap)
    await db.commit()
    return {"message": "스크랩이 취소되었습니다."}
