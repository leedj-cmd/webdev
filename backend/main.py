from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.routers import auth,post
import app.models.user  
import app.models.post


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # 서버 시작 시 테이블 자동 생성
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(post.router)



@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "서버가 정상적으로 켜졌습니다!"}