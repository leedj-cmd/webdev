from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 작성/수정 시간 자동 기록
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    view_count = Column(Integer, default=0, nullable=False)

    # 관계 설정
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    recommends = relationship("PostRecommend", back_populates="post", cascade="all, delete-orphan")
    bookmarks = relationship("PostBookmark", back_populates="post", cascade="all, delete-orphan")
    scraps = relationship("Scrap", back_populates="post", cascade="all, delete-orphan")
