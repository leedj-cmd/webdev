from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CommunityLike(Base):
    __tablename__ = "community_likes"    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    community_id = Column(Integer, ForeignKey("communities.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="community_likes")
    community = relationship("Community", back_populates="likes")

class CommunityCommentLike(Base):
    __tablename__ = "community_comment_likes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    comment_id = Column(Integer, ForeignKey("community_comments.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="community_comment_likes")
    comment = relationship("CommunityComment", back_populates="likes")