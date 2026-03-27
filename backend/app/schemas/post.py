from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# 1. 공통으로 들어갈 내용
class PostBase(BaseModel):
    title: str
    content: str
    file_url: Optional[str] = None  # 첨부파일은 없을 수도 있으니 Optional 처리

# 2. 글 작성용 상자 (클라이언트 -> 서버)
class PostCreate(PostBase):
    pass  # PostBase의 내용(제목, 내용, 파일)을 그대로 물려받아 사용합니다.

# 3. 글 수정용 상자 (클라이언트 -> 서버)
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    file_url: Optional[str] = None

# 4. 프론트엔드로 보내줄 완성된 포장 상자 (서버 -> 클라이언트)
class PostResponse(PostBase):
    id: int
    view_count: int
    created_at: datetime
    author_id: int

    model_config = ConfigDict(from_attributes=True)
