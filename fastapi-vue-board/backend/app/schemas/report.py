from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    reason: str  # 신고 사유 직접 입력

class ReportResponse(BaseModel):
    id: int
    post_id: int
    reporter_id: int
    reason: str
    is_resolved: bool
    resolved_by: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}