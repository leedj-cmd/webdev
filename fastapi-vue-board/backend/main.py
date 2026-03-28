from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, post, comment, interaction
import app.models.user
import app.models.post
import app.models.comment
import app.models.interaction

app = FastAPI(title="DevCareer API")

# CORS 설정 (Vue.js 연결 필수!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(interaction.router)

@app.get("/")
def health_check():
    return {"status": "ok"}