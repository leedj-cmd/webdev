# filename: backend/app/schemas/scrap.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.job import JobResponse
from app.schemas.contest import ContestResponse

class ScrapCreate(BaseModel):
    scrap_type: str        # "job" 또는 "contest"
    target_id: int         # 스크랩할 job_id 또는 contest_id
    title: Optional[str] = None
    subtitle: Optional[str] = None
    external_url: Optional[str] = None
    is_external: bool = False

class ScrapResponse(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int] = None
    contest_id: Optional[int] = None
    scrap_type: str
    external_id: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    external_url: Optional[str] = None
    created_at: datetime
    job: Optional[JobResponse] = None
    contest: Optional[ContestResponse] = None

    model_config = {"from_attributes": True}
