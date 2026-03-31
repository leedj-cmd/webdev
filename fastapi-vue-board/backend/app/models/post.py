from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    
    # 필터링을 위한 컬럼 (직무별 / 지역별)
    job_category = Column(String, index=True, nullable=True) 
    region = Column(String, index=True, nullable=True)       
    
    # 작성자 ID (User 테이블과 연결)
    # 주의: User 모델의 __tablename__이 "users"가 맞는지 확인해주세요!
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 작성/수정 시간 자동 기록
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())