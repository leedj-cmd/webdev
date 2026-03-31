# filename: backend/app/models/job.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    
    # 공고 기본 정보
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)       # 회사명
    description = Column(Text, nullable=False)                  # 상세내용
    
    # 필터링용 컬럼
    job_category = Column(String, nullable=True, index=True)   # 직무 카테고리
    region = Column(String, nullable=True, index=True)         # 근무지역
    experience = Column(String, nullable=True)                 # 경력 (신입/경력/무관)
    education = Column(String, nullable=True)                  # 학력
    
    # 공고 기간
    deadline = Column(DateTime(timezone=True), nullable=True)  # 마감일
    
    # 외부 링크 (원문 공고 URL)
    external_url = Column(String, nullable=True)
    
    # 관리자 ID (등록한 관리자)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 활성화 여부 (비활성화로 숨김 처리)
    is_active = Column(Boolean, default=True)
    
    # 작성/수정 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())