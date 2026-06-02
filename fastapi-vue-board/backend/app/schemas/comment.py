from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    parent_id: Optional[int] = None  # 대댓글일 경우 부모 댓글 ID (원본 댓글이면 안 넣어도 됨)

class CommentUpdate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True} # DB 모델을 Pydantic으로 자동 변환해주는 마법의 설정