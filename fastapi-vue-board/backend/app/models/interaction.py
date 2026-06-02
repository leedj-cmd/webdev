from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# 좋아요 모델
class PostLike(Base):
    __tablename__ = "post_likes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")

# 북마크 모델
class PostBookmark(Base):
    __tablename__ = "post_bookmarks"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="post_bookmarks") # User 모델에도 추가 필요할 수 있음
    post = relationship("Post", back_populates="bookmarks")

# 추천 모델
class PostRecommend(Base):
    __tablename__ = "post_recommends"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="post_recommends")
    post = relationship("Post", back_populates="recommends")
