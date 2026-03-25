from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.routers import auth
import app.models.user  # 테이블 인식을 위해 import


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # 서버 시작 시 테이블 자동 생성
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
