import asyncio
from app.database import engine, Base

# 👇👇👇 이 두 줄을 추가해 주세요! (기존 테이블 설계도도 가져오기)
from app.models.user import User  # (주의: 파일 이름이 users.py라면 app.models.users 로 수정!)
from app.models.post import Post

# 새로 만든 테이블들
from app.models.comment import Comment
from app.models.interaction import PostLike, PostRecommend

async def init_db():
    print("🚀 데이터베이스 테이블 생성을 시작합니다...")
    async with engine.begin() as conn:
        # 모든 테이블 설계도를 모아서 DB에 쏴줍니다.
        await conn.run_sync(Base.metadata.create_all)
    print("✨ 테이블 생성 완료! 이제 서버를 켜도 좋습니다.")

if __name__ == "__main__":
    asyncio.run(init_db())