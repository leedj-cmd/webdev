from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 1. 회원가입
@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 이메일 중복 확인
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 사용중인 이메일입니다")

    # 유저 생성
    new_user = User(
        email=data.email,
        username=data.username,
        hashed_password=pwd_context.hash(data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# 2. 로그인
@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    # 유저 확인
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")

    # 토큰 발급
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}