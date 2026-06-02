from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQResponse(FAQBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class FAQQuery(BaseModel):
    query: str

class FAQQueryResult(BaseModel):
    question: str
    answer: str
    score: float
