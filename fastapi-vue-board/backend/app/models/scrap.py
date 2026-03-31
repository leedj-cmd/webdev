# filename: backend/app/models/scrap.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Scrap(Base):
    __tablename__ = "scraps"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # job_id 또는 contest_id 중 하나만 값이 들어옴
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=True)
    
    # 어떤 타입인지 명시 ("job" or "contest")
    scrap_type = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())