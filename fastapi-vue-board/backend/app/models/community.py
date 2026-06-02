from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# 1. 커뮤니티 게시글
class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="communities")
    comments = relationship("CommunityComment", back_populates="community", cascade="all, delete-orphan")
    likes = relationship("CommunityLike", back_populates="community", cascade="all, delete-orphan")


# 2. 커뮤니티 참여자
class CommunityParticipant(Base):
    __tablename__ = "community_participants"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())


# 3. 댓글 + 대댓글
class CommunityComment(Base):
    __tablename__ = "community_comments"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    parent_id = Column(Integer, ForeignKey("community_comments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    community = relationship("Community", back_populates="comments")
    author = relationship("User", back_populates="community_comments")
    replies = relationship("CommunityComment", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("CommunityComment", back_populates="replies", remote_side="CommunityComment.id")
    likes = relationship("CommunityCommentLike", back_populates="comment", cascade="all, delete-orphan")