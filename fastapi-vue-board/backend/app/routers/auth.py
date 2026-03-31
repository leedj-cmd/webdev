# filename: backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token,
    FindIdRequest, FindPasswordRequest, ResetPasswordRequest,
    UpdateProfileRequest, DeleteAccountRequest
)
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import List
import os
import shutil

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ── 토큰 생성 함수
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ── 현재 유저 가져오는 함수 (다른 API에서도 재사용)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    return user

# ── 1. 회원가입
@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 사용중인 이메일입니다")

    new_user = User(
        email=data.email,
        username=data.username,
        hashed_password=pwd_context.hash(data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# ── 2. 로그인
@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# ── 3. 로그아웃
@router.post("/logout")
async def logout():
    return {"message": "로그아웃 되었습니다"}

# ── 4. 토큰 재발급
@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    new_token = create_access_token({"sub": str(current_user.id)})
    return {"access_token": new_token, "token_type": "bearer"}

# ── 5. 아이디 찾기 (username으로 email 찾기)
@router.post("/find-id")
async def find_id(data: FindIdRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="해당 닉네임의 유저를 찾을 수 없습니다")
    # 이메일 일부 가려서 반환
    email = user.email
    hidden = email[2:email.index("@")]
    masked_email = email[:2] + "*" * len(hidden) + email[email.index("@"):]
    return {"email": masked_email}

# ── 6. 비밀번호 찾기 (이메일로 임시 비밀번호 발송)
@router.post("/find-password")
async def find_password(data: FindPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="해당 이메일의 유저를 찾을 수 없습니다")
    # 실제 서비스에서는 이메일 발송 라이브러리 사용
    # 지금은 임시로 메시지만 반환
    return {"message": f"{data.email} 로 임시 비밀번호를 발송했습니다"}

# ── 7. 비밀번호 재설정
@router.patch("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    user.hashed_password = pwd_context.hash(data.new_password)
    await db.commit()
    return {"message": "비밀번호가 재설정되었습니다"}

# ── 8. 로그인 상태 확인 (내 정보 조회)
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ── 9. 프로필 조회
@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ── 10. 프로필 수정
@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if data.username:
        current_user.username = data.username
    await db.commit()
    await db.refresh(current_user)
    return current_user

# ── 11. 프로필 이미지 업로드
@router.post("/profile/image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 이미지 저장 폴더 생성
    os.makedirs("uploads/profile", exist_ok=True)

    # 파일 저장
    file_path = f"uploads/profile/{current_user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # DB에 이미지 경로 저장
    current_user.profile_image = file_path
    await db.commit()
    return {"message": "프로필 이미지가 업로드되었습니다", "path": file_path}

# ── 12. 회원 탈퇴
@router.delete("/me")
async def delete_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 비밀번호 확인
    if not pwd_context.verify(data.password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다")

    await db.delete(current_user)
    await db.commit()
    return {"message": "회원 탈퇴가 완료되었습니다"}

# ── 13. 활동 내역 조회
@router.get("/activity")
async def get_activity(current_user: User = Depends(get_current_user)):
    # 나중에 posts, comments 테이블과 연결
    return {
        "user_id": current_user.id,
        "message": "활동 내역 조회 (게시글/댓글 모델 연결 후 구현)"
    }

# ── 14. 추천 목록 조회
@router.get("/likes")
async def get_likes(current_user: User = Depends(get_current_user)):
    # 나중에 likes 테이블과 연결
    return {
        "user_id": current_user.id,
        "message": "추천 목록 조회 (좋아요 모델 연결 후 구현)"
    }

# ── 15. 관리자 전용 회원가입 (비밀 코드 필요)
@router.post("/signup/admin", response_model=UserResponse, status_code=201)
async def signup_admin(
    data: UserCreate,
    admin_secret: str,           # Swagger에서 쿼리 파라미터로 입력
    db: AsyncSession = Depends(get_db)
):
    # .env의 ADMIN_SECRET과 비교 (없으면 기본값 사용)
    if admin_secret != os.getenv("ADMIN_SECRET", "admin_secret_change_me"):
        raise HTTPException(status_code=403, detail="관리자 코드가 틀렸습니다.")

    # 이메일 중복 확인
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 사용중인 이메일입니다")

    # role을 "admin"으로 설정해서 생성
    new_user = User(
        email=data.email,
        username=data.username,
        hashed_password=pwd_context.hash(data.password),
        role="admin"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# ── 16. 기존 유저를 관리자로 승격 (비밀 코드 필요)
@router.patch("/promote/admin")
async def promote_to_admin(
    email: str,
    admin_secret: str,
    db: AsyncSession = Depends(get_db)
):
    if admin_secret != os.getenv("ADMIN_SECRET", "admin_secret_change_me"):
        raise HTTPException(status_code=403, detail="관리자 코드가 틀렸습니다.")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    user.role = "admin"
    await db.commit()
    return {"message": f"{email} 계정이 관리자로 승격되었습니다."}