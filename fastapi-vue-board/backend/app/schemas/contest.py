# filename: backend/app/schemas/contest.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContestBase(BaseModel):
    title: str
    organizer: str
    description: str
    category: Optional[str] = None
    target: Optional[str] = None
    prize: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    external_url: Optional[str] = None

class ContestCreate(ContestBase):
    pass

class ContestUpdate(BaseModel):
    title: Optional[str] = None
    organizer: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target: Optional[str] = None
    prize: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    external_url: Optional[str] = None
    is_active: Optional[bool] = None

class ContestResponse(ContestBase):
    id: int
    author_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    scrap_count: Optional[int] = 0

    model_config = {"from_attributes": True}