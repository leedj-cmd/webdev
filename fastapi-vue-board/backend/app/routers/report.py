from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.report import Report, CommunityReport
from app.models.user import User
from app.schemas.report import ReportCreate, ReportResponse
from app.schemas.community import CommunityReportCreate, CommunityReportResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

# 1. 게시글 신고 (로그인 필요, 중복 신고 방지)
@router.post("/posts/{post_id}", response_model=ReportResponse)
async def report_post(
    post_id: int,
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Report).where(
            Report.post_id == post_id,
            Report.reporter_id == current_user.id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 신고한 게시글입니다.")

    new_report = Report(
        post_id=post_id,
        reporter_id=current_user.id,
        reason=data.reason
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report


# 2. 커뮤니티 글 신고 (로그인 필요, 중복 신고 방지)
@router.post("/community/{community_id}", response_model=CommunityReportResponse)
async def report_community(
    community_id: int,
    data: CommunityReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CommunityReport).where(
            CommunityReport.community_id == community_id,
            CommunityReport.reporter_id == current_user.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 신고한 게시글입니다.")

    new_report = CommunityReport(
        community_id=community_id,
        reporter_id=current_user.id,
        reason=data.reason,
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report