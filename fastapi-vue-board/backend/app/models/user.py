from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 1. 일반 게시판 관계
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    post_recommends = relationship("PostRecommend", back_populates="user", cascade="all, delete-orphan")
    post_bookmarks = relationship("PostBookmark", back_populates="user", cascade="all, delete-orphan")
    scraps = relationship("Scrap", back_populates="user", cascade="all, delete-orphan")
    
    # 2. 커뮤니티 관계
    communities = relationship("Community", back_populates="owner")
    community_comments = relationship("CommunityComment", back_populates="author")
    community_likes = relationship("CommunityLike", back_populates="user")
    community_comment_likes = relationship("CommunityCommentLike", back_populates="user")
    
    # 3. 채팅 및 시스템 관계
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    chat_memberships = relationship("ChatMember", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="sender", cascade="all, delete-orphan")
