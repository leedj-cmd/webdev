from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, post, comment, interaction, job, contest
import app.models.user
import app.models.post
import app.models.comment
import app.models.interaction

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # 서버 시작 시 테이블 자동 생성
    yield

app = FastAPI(title="DevCareer API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(interaction.router)
app.include_router(job.router)
app.include_router(contest.router)

@app.get("/")
def health_check():
    return {"status": "ok"}
