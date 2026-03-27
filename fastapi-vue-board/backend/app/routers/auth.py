from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login():
    return {"message": "로그인 기능 준비 중"}

@router.post("/signup")
async def signup():
    return {"message": "회원가입 기능 준비 중"}