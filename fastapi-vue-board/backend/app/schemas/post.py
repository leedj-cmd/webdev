from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 공통 속성
class PostBase(BaseModel):
    title: str
    content: str
    job_category: Optional[str] = None
    region: Optional[str] = None

# 1. 생성할 때 받는 데이터
class PostCreate(PostBase):
    author_id: int  # 나중에는 토큰에서 가져오게 수정하는 것이 좋습니다.

# 2. 수정할 때 받는 데이터 (모든 필드가 선택적)
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    job_category: Optional[str] = None
    region: Optional[str] = None

# 3. 응답할 때 보내주는 데이터
class PostResponse(PostBase):
    id: int
    author_id: int
    author_name: Optional[str] = None  # ← 추가
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0  # ← 추가
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True