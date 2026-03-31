from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    FindIdRequest, FindPasswordRequest, ResetPasswordRequest,
    UpdateProfileRequest, DeleteAccountRequest
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
import os
import shutil

router = APIRouter(prefix="/auth", tags=["Auth"])

# ── 현재 유저 가져오기
async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
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
        password=hash_password(data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# ── 2. 로그인
@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")
    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
        "token_type": "bearer"
    }

# ── 3. 로그아웃
@router.post("/logout")
async def logout():
    return {"message": "로그아웃 되었습니다"}

# ── 4. 토큰 재발급
@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
        user_id = payload.get("sub")
        return {
            "access_token": create_access_token({"sub": user_id}),
            "refresh_token": create_refresh_token({"sub": user_id}),
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="만료되거나 유효하지 않은 토큰입니다")

# ── 5. 아이디 찾기
@router.post("/find-id")
async def find_id(data: FindIdRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="해당 닉네임의 유저를 찾을 수 없습니다")
    email = user.email
    hidden = email[2:email.index("@")]
    masked_email = email[:2] + "*" * len(hidden) + email[email.index("@"):]
    return {"email": masked_email}

# ── 6. 비밀번호 찾기
@router.post("/find-password")
async def find_password(data: FindPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="해당 이메일의 유저를 찾을 수 없습니다")
    return {"message": f"{data.email} 로 임시 비밀번호를 발송했습니다"}

# ── 7. 비밀번호 재설정
@router.patch("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    user.password = hash_password(data.new_password)
    await db.commit()
    return {"message": "비밀번호가 재설정되었습니다"}

# ── 8. 내 정보 조회
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ── 9. 프로필 수정
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

# ── 10. 프로필 이미지 업로드
@router.post("/profile/image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    os.makedirs("uploads/profile", exist_ok=True)
    file_path = f"uploads/profile/{current_user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    current_user.profile_image = file_path
    await db.commit()
    return {"message": "프로필 이미지가 업로드되었습니다", "path": file_path}

# ── 11. 회원 탈퇴
@router.delete("/me")
async def delete_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(data.password, current_user.password):
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다")
    await db.delete(current_user)
    await db.commit()
    return {"message": "회원 탈퇴가 완료되었습니다"}

# ── 12. 관리자 회원가입
@router.post("/signup/admin", response_model=UserResponse, status_code=201)
async def signup_admin(data: UserCreate, admin_secret: str, db: AsyncSession = Depends(get_db)):
    if admin_secret != os.getenv("ADMIN_SECRET", "admin_secret_change_me"):
        raise HTTPException(status_code=403, detail="관리자 코드가 틀렸습니다.")
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 사용중인 이메일입니다")
    new_user = User(
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        role="admin"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# ── 13. 관리자 승격
@router.patch("/promote/admin")
async def promote_to_admin(email: str, admin_secret: str, db: AsyncSession = Depends(get_db)):
    if admin_secret != os.getenv("ADMIN_SECRET", "admin_secret_change_me"):
        raise HTTPException(status_code=403, detail="관리자 코드가 틀렸습니다.")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    user.role = "admin"
    await db.commit()
    return {"message": f"{email} 계정이 관리자로 승격되었습니다."}
