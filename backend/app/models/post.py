from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Post(Base):
    __tablename__ = "posts" # 데이터베이스에 만들어질 실제 테이블 이름

    # 1. 기본 정보
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)             # 제목 (빠른 검색을 위해 index=True)
    content = Column(Text, nullable=False)                         # 내용
    view_count = Column(Integer, default=0)                        # 조회수 (글을 처음 쓰면 0부터 시작)
    file_url = Column(String, nullable=True)                       # 첨부파일 경로 (파일이 없을 수도 있으니 nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 작성일 (서버 시간으로 자동 기록)
    
    # 2. 작성자 정보 (User 테이블과 연결)
    author_id = Column(Integer, ForeignKey("users.id"))            # 글쓴이의 회원 번호
    author = relationship("User", back_populates="posts")         
