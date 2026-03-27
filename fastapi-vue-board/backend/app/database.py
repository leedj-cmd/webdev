import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. .env 파일에 있는 비밀 수첩 내용을 불러옵니다!
load_dotenv()

# 2. 수첩에서 DATABASE_URL 값을 꺼내옵니다.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# (혹시 .env 설정 빼먹은 팀원이 있으면 알려주기 위한 방어 코드)
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("🚨 .env 파일에 DATABASE_URL을 설정해주세요!")

# 3. DB 엔진 생성
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# 4. 세션 팩토리 생성
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 5. 베이스 모델
Base = declarative_base()

# 6. DB 세션 가져오기
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session