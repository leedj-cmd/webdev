import asyncio
from app.database import engine, Base

# 모든 모델 import (테이블 설계도 등록)
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.interaction import PostLike, PostRecommend
from app.models.job import Job
from app.models.contest import Contest
from app.models.scrap import Scrap

async def init_db():
    print("🗑️  기존 테이블을 전부 삭제합니다...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ 기존 테이블 삭제 완료!")

    print("🚀 테이블을 새로 생성합니다...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✨ 테이블 생성 완료! 이제 서버를 켜도 좋습니다.")

if __name__ == "__main__":
    asyncio.run(init_db())