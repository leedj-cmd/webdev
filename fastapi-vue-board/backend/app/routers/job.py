# filename: backend/app/routers/job.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.database import get_db
from app.models.job import Job
from app.models.scrap import Scrap
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.external_opportunities import fetch_external_jobs

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ── 관리자 확인 헬퍼 함수
def require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")

# 1. 채용공고 목록 조회 + 검색 + 필터링
@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 10,
    include_external: bool = True,
    external_limit: int = 30,
    search: Optional[str] = Query(None, description="제목/회사명/키워드 검색"),
    job_category: Optional[str] = Query(None, description="직무 카테고리 필터"),
    region: Optional[str] = Query(None, description="지역 필터"),
    experience: Optional[str] = Query(None, description="경력 필터"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).where(Job.is_active == True)

    if search:
        query = query.where(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%"),
                Job.job_category.ilike(f"%{search}%")
            )
        )
    if job_category:
        query = query.where(Job.job_category == job_category)
    if region:
        query = query.where(Job.region == region)
    if experience:
        query = query.where(Job.experience == experience)

    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    jobs = list(result.scalars().all())

    if not include_external:
        return jobs

    external_jobs = await fetch_external_jobs(limit=min(max(external_limit, 0), 50))
    if search:
        lowered = search.lower()
        external_jobs = [
            job for job in external_jobs
            if any(lowered in str(job.get(field) or "").lower() for field in ["title", "company", "description", "job_category"])
        ]
    if job_category:
        external_jobs = [
            job for job in external_jobs
            if job_category in (job.get("job_category") or "") or job_category in (job.get("description") or "")
        ]
    if region:
        external_jobs = [
            job for job in external_jobs
            if region.lower() in (job.get("region") or "").lower()
        ]
    if experience:
        external_jobs = [
            job for job in external_jobs
            if experience in (job.get("experience") or "")
        ]

    return jobs + external_jobs

# 2. 채용공고 상세 조회
@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다.")
    return job

# 3. 채용공고 등록 (관리자만)
@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    new_job = Job(**data.model_dump(), author_id=current_user.id)
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job

# 4. 채용공고 수정 (관리자만)
@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)

    await db.commit()
    await db.refresh(job)
    return job

# 5. 채용공고 삭제 (관리자만) - is_active=False 처리 (소프트 삭제)
@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다.")

    job.is_active = False
    await db.commit()
    return {"message": "채용공고가 비활성화되었습니다."}

# 6. 스크랩 추가
@router.post("/{job_id}/scrap")
async def scrap_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 중복 체크
    query = select(Scrap).where(Scrap.job_id == job_id, Scrap.user_id == current_user.id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 스크랩한 공고입니다.")

    new_scrap = Scrap(user_id=current_user.id, job_id=job_id, scrap_type="job")
    db.add(new_scrap)
    await db.commit()
    return {"message": "스크랩되었습니다."}

# 7. 스크랩 취소
@router.delete("/{job_id}/scrap")
async def unscrap_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Scrap).where(Scrap.job_id == job_id, Scrap.user_id == current_user.id)
    result = await db.execute(query)
    scrap = result.scalar_one_or_none()
    if not scrap:
        raise HTTPException(status_code=404, detail="스크랩 기록이 없습니다.")

    await db.delete(scrap)
    await db.commit()
    return {"message": "스크랩이 취소되었습니다."}
