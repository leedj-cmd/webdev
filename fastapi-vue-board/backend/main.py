# filename: backend/main.py
from fastapi import FastAPI
<<<<<<< Updated upstream

app = FastAPI()


=======
from app.database import init_db
from app.routers import auth, post
import app.models.user  # 테이블 인식을 위해 import
import app.models.post  # 테이블 인식을 위해 import

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # 서버 시작 시 테이블 자동 생성
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(post.router)
>>>>>>> Stashed changes

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/hello")
def hello():
    return {"message": "Hello, FastAPI!"}

#데이터 조회 (http://127.0.0.1:8000/posts)
@app.get("/posts")
def list_post():
    return {"posts": [{"id": 1, "title": "첫 번째 글"}]}


#데이터 생성 (http://127.0.0.1:8000/posts)
@app.post("/posts")
def create_post():
    return {"message": "게시글이 생성되었습니다"}

#데이터 수정 (http://127.0.0.1:8000/posts/1)
@app.put("/posts/{post_id}")
def update_post(post_id: int):
    return {"message": f"{post_id}번 게시글이 수정되었습니다"}

#데이터 삭제 (http://127.0.0.1:8000/posts/1)
@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    return {"message": f"{post_id}번 게시글이 삭제되었습니다"}



