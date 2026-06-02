from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.models.post import Post
from app.schemas.user import UserResponse
from app.schemas.report import ReportResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

def require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")

# 1. 유저 목록 조회 (관리자만)
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

# 2. 유저 정지 (관리자만)
@router.patch("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="관리자는 정지할 수 없습니다.")

    user.is_suspended = True
    await db.commit()
    return {"message": f"{user.username} 계정이 정지되었습니다."}

# 3. 유저 정지 해제 (관리자만)
@router.patch("/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    user.is_suspended = False
    await db.commit()
    return {"message": f"{user.username} 계정 정지가 해제되었습니다."}

# 4. 신고 목록 조회 (관리자만)
@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 20,
    is_resolved: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(
        select(Report)
        .where(Report.is_resolved == is_resolved)
        .order_by(Report.created_at.desc())
        .offset(skip).limit(limit)
    )
    return result.scalars().all()

# 5. 신고 처리 - 게시글 삭제 없이 신고만 해결 (관리자만)
@router.patch("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="신고를 찾을 수 없습니다.")
    if report.is_resolved:
        raise HTTPException(status_code=400, detail="이미 처리된 신고입니다.")

    report.is_resolved = True
    report.resolved_by = current_user.id
    report.resolved_at = datetime.utcnow()
    await db.commit()
    return {"message": "신고가 처리되었습니다."}

# 6. 신고 처리 - 게시글 삭제 후 신고 해결 (관리자만)
@router.delete("/reports/{report_id}/resolve-and-delete")
async def resolve_and_delete_post(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    require_admin(current_user)
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="신고를 찾을 수 없습니다.")
    if report.is_resolved:
        raise HTTPException(status_code=400, detail="이미 처리된 신고입니다.")

    # 게시글 삭제
    post_result = await db.execute(select(Post).where(Post.id == report.post_id))
    post = post_result.scalar_one_or_none()
    if post:
        await db.delete(post)

    # 신고 처리
    report.is_resolved = True
    report.resolved_by = current_user.id
    report.resolved_at = datetime.utcnow()
    await db.commit()
    return {"message": "게시글이 삭제되고 신고가 처리되었습니다."}