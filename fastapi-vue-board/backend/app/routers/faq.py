from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQResponse, FAQQuery
from app.services.ai_service import ai_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/faq", tags=["FAQ"])

@router.post("/", response_model=FAQResponse)
async def create_faq(
    data: FAQCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 FAQ를 등록할 수 있습니다.")
    
    faq = FAQ(**data.model_dump())
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    return faq

@router.get("/", response_model=List[FAQResponse])
async def get_faqs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FAQ))
    return result.scalars().all()

@router.post("/ask")
async def ask_ai(query_data: FAQQuery):
    """DB 검색이 아닌 Gemini AI가 직접 답변 생성"""
    answer = await ai_service.get_ai_response(query_data.query)
    
    return {
        "question": query_data.query,
        "answer": answer,
        "score": 1.0  # 생성형이므로 점수는 고정값 또는 생략 가능
    }

@router.post("/check-censorship")
async def check_censorship(text_data: dict, current_user: User = Depends(get_current_user)):
    text = text_data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="텍스트가 없습니다.")
    
    result = ai_service.check_censorship(text)
    return result
