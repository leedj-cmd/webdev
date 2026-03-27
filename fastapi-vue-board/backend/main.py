# filename: backend/main.py
from fastapi import FastAPI
from app.routers import auth, post, comment, interaction
import app.models.user
import app.models.post
import app.models.comment
import app.models.interaction

app = FastAPI()

app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(interaction.router)

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