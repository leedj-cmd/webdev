# filename: backend/app/schemas/scrap.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScrapCreate(BaseModel):
    scrap_type: str        # "job" 또는 "contest"
    target_id: int         # 스크랩할 job_id 또는 contest_id

class ScrapResponse(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int] = None
    contest_id: Optional[int] = None
    scrap_type: str
    created_at: datetime

    model_config = {"from_attributes": True}