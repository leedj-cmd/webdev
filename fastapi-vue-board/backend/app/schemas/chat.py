from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.chat import RoomType

# ── 유저 요약 정보 (채팅방 목록용)
class UserMinimal(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# ── 채팅방 생성 요청
class ChatRoomCreate(BaseModel):
    name: Optional[str] = None          # 그룹 채팅방 이름 (1:1은 생략)
    type: RoomType = RoomType.direct
    member_ids: List[int]               # 초대할 상대방 user_id 목록

# ── 참여자 응답
class ChatMemberResponse(BaseModel):
    user_id: int
    joined_at: datetime
    user: Optional[UserMinimal] = None  # 유저 정보 포함

    class Config:
        from_attributes = True

# ── 채팅방 응답
class ChatRoomResponse(BaseModel):
    id: int
    name: Optional[str]
    type: RoomType
    created_by: Optional[int]
    created_at: datetime
    members: List[ChatMemberResponse] = []
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0

    class Config:
        from_attributes = True

# ── 메시지 응답
class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: Optional[int]
    content: str
    message_type: str = "text"
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_content_type: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
