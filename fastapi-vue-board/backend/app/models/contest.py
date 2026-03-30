# filename: backend/app/models/contest.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    
    # 공모전 기본 정보
    title = Column(String, nullable=False, index=True)
    organizer = Column(String, nullable=False)                  # 주최기관
    description = Column(Text, nullable=False)
    
    # 필터링용 컬럼
    category = Column(String, nullable=True, index=True)        # 분야 (디자인/기획/IT 등)
    target = Column(String, nullable=True)                      # 대상 (대학생/일반인 등)
    prize = Column(String, nullable=True)                       # 시상내역
    
    # 공모전 기간
    start_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    # 외부 링크
    external_url = Column(String, nullable=True)
    
    # 관리자 ID
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())