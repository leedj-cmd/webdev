from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RoomType(str, enum.Enum):
    direct = "direct"   # 1:1 채팅
    group  = "group"    # 그룹 채팅

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=True)          # 그룹 채팅방 이름 (1:1은 None)
    type       = Column(Enum(RoomType), default=RoomType.direct, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members  = relationship("ChatMember", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")

class ChatMember(Base):
    __tablename__ = "chat_members"

    id        = Column(Integer, primary_key=True, index=True)
    room_id   = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id   = Column(Integer, ForeignKey("users.id",      ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("ChatRoom", back_populates="members")
    user = relationship("User",     back_populates="chat_memberships")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    room_id    = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id  = Column(Integer, ForeignKey("users.id",      ondelete="SET NULL"), nullable=True)
    content    = Column(Text, nullable=False)
    message_type = Column(String(20), default="text", nullable=False)
    file_url   = Column(String(500), nullable=True)
    file_name  = Column(String(255), nullable=True)
    file_size  = Column(Integer, nullable=True)
    file_content_type = Column(String(100), nullable=True)
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room   = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User",     back_populates="messages")
