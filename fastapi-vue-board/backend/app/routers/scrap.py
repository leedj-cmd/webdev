from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.contest import Contest
from app.models.job import Job
from app.models.scrap import Scrap
from app.schemas.scrap import ScrapCreate, ScrapResponse
# 다른 파일들과 형식을 맞춥니다.
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scraps", tags=["Scraps"])

# 1. 스크랩 추가
@router.post("/", response_model=ScrapResponse)
async def add_scrap(
    data: ScrapCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if data.scrap_type not in {"job", "contest"}:
        raise HTTPException(status_code=400, detail="스크랩 유형이 올바르지 않습니다.")

    is_external = data.is_external or data.target_id < 0

    # 중복 체크
    if is_external:
        external_id = str(data.target_id)
        query = select(Scrap).where(
            Scrap.user_id == current_user.id,
            Scrap.scrap_type == data.scrap_type,
            Scrap.external_id == external_id,
        )
    elif data.scrap_type == "job":
        target_result = await db.execute(select(Job).where(Job.id == data.target_id, Job.is_active.is_(True)))
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다.")
        query = select(Scrap).where(Scrap.user_id == current_user.id, Scrap.job_id == data.target_id)
    else:
        target_result = await db.execute(select(Contest).where(Contest.id == data.target_id, Contest.is_active.is_(True)))
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="공모전을 찾을 수 없습니다.")
        query = select(Scrap).where(Scrap.user_id == current_user.id, Scrap.contest_id == data.target_id)
    
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 스크랩한 항목입니다.")

    scrap = Scrap(
        user_id=current_user.id,
        job_id=data.target_id if data.scrap_type == "job" and not is_external else None,
        contest_id=data.target_id if data.scrap_type == "contest" and not is_external else None,
        scrap_type=data.scrap_type,
        external_id=str(data.target_id) if is_external else None,
        title=data.title.strip() if data.title else None,
        subtitle=data.subtitle.strip() if data.subtitle else None,
        external_url=data.external_url.strip() if data.external_url else None,
    )
    db.add(scrap)
    await db.commit()
    await db.refresh(scrap)
    result = await db.execute(
        select(Scrap)
        .options(selectinload(Scrap.job), selectinload(Scrap.contest))
        .where(Scrap.id == scrap.id)
    )
    return result.scalar_one()

# 2. 내 스크랩 목록 조회
@router.get("/", response_model=List[ScrapResponse])
async def get_my_scraps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Scrap)
        .options(selectinload(Scrap.job), selectinload(Scrap.contest))
        .where(Scrap.user_id == current_user.id)
        .order_by(Scrap.created_at.desc(), Scrap.id.desc())
    )
    return result.scalars().all()

# 3. 스크랩 취소
@router.delete("/{scrap_id}")
async def delete_scrap(
    scrap_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Scrap).where(Scrap.id == scrap_id, Scrap.user_id == current_user.id))
    scrap = result.scalar_one_or_none()
    if not scrap:
        raise HTTPException(status_code=404, detail="스크랩을 찾을 수 없습니다.")
    await db.delete(scrap)
    await db.commit()
    return {"message": "스크랩이 취소되었습니다."}

# 4. 스크랩 여부 확인
@router.get("/check")
async def check_scrap(
    scrap_type: str,
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if scrap_type not in {"job", "contest"}:
        raise HTTPException(status_code=400, detail="스크랩 유형이 올바르지 않습니다.")

    if scrap_type == "job":
        query = select(Scrap).where(Scrap.user_id == current_user.id, Scrap.job_id == target_id)
    else:
        query = select(Scrap).where(Scrap.user_id == current_user.id, Scrap.contest_id == target_id)
    
    result = await db.execute(query)
    scrap = result.scalar_one_or_none()
    return {"scrapped": scrap is not None, "scrap_id": scrap.id if scrap else None}
