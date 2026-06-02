from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401 - register SQLAlchemy models before create_all
from app.database import init_db
from app.routers import auth, post, comment, interaction, job, contest, scrap, admin, chat, notification, report, community, faq
from app.services.ai_service import ai_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # 서버 시작 시 테이블 자동 생성
    # AI 모델 미리 로드
    import asyncio
    asyncio.create_task(asyncio.to_thread(ai_service.load_models))
    yield

app = FastAPI(title="DevCareer API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드된 정적 파일 서빙
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(interaction.router)
app.include_router(job.router)
app.include_router(contest.router)
app.include_router(scrap.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(notification.router)
app.include_router(report.router)
app.include_router(community.router)
app.include_router(faq.router)

@app.get("/")
def health_check():
    return {"status": "ok"}
