from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.database import get_db
# 모델 경로는 이미 만들어두신 app/models/interaction.py를 참조합니다.
from app.models.interaction import PostLike, PostRecommend 

router = APIRouter(prefix="/interactions", tags=["Interactions"])

# 요청 시 받을 데이터 형식 (유저 ID)
class InteractionRequest(BaseModel):
    user_id: int

# --- [ 좋아요(Like) 기능 ] ---

# 1. 좋아요 추가
@router.post("/{post_id}/likes")
async def add_like(post_id: int, req: InteractionRequest, db: AsyncSession = Depends(get_db)):
    # 중복 체크 (이미 좋아요를 눌렀는지 확인)
    query = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == req.user_id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 좋아요를 누르셨습니다.")
    
    new_like = PostLike(post_id=post_id, user_id=req.user_id)
    db.add(new_like)
    await db.commit()
    return {"message": "좋아요가 추가되었습니다."}

# 2. 좋아요 취소
@router.delete("/{post_id}/likes/{user_id}")
async def remove_like(post_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == user_id)
    result = await db.execute(query)
    like = result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(status_code=404, detail="좋아요 기록이 없습니다.")
    
    await db.delete(like)
    await db.commit()
    return {"message": "좋아요가 취소되었습니다."}


# --- [ 추천(Recommend) 기능 ] ---

# 3. 추천 추가
@router.post("/{post_id}/recommends")
async def add_recommend(post_id: int, req: InteractionRequest, db: AsyncSession = Depends(get_db)):
    # 중복 체크
    query = select(PostRecommend).where(PostRecommend.post_id == post_id, PostRecommend.user_id == req.user_id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 추천하셨습니다.")
    
    new_rec = PostRecommend(post_id=post_id, user_id=req.user_id)
    db.add(new_rec)
    await db.commit()
    return {"message": "추천되었습니다."}

# 4. 추천 취소
@router.delete("/{post_id}/recommends/{user_id}")
async def remove_recommend(post_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PostRecommend).where(PostRecommend.post_id == post_id, PostRecommend.user_id == user_id)
    result = await db.execute(query)
    recommend = result.scalar_one_or_none()
    
    if not recommend:
        raise HTTPException(status_code=404, detail="추천 기록이 없습니다.")
    
    await db.delete(recommend)
    await db.commit()
    return {"message": "추천이 취소되었습니다."}