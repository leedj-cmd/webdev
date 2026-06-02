# filename: backend/app/schemas/job.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    job_category: Optional[str] = None
    region: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    deadline: Optional[datetime] = None
    external_url: Optional[str] = None

# 생성할 때 (관리자만)
class JobCreate(JobBase):
    pass

# 수정할 때 (모든 필드 선택적)
class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    job_category: Optional[str] = None
    region: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    deadline: Optional[datetime] = None
    external_url: Optional[str] = None
    is_active: Optional[bool] = None

# 응답할 때
class JobResponse(JobBase):
    id: int
    author_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    scrap_count: Optional[int] = 0   # 스크랩 수 (나중에 확장용)
    is_external: bool = False
    source: Optional[str] = None

    model_config = {"from_attributes": True}
