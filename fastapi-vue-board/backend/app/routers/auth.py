from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
import smtplib

from app.database import get_db
from app.models.email_verification import EmailVerificationToken
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    FindIdRequest, FindPasswordRequest, ResetPasswordRequest,
    ResendVerificationRequest,
    ResetPasswordWithCurrentRequest,
    UpdateProfileRequest, ChangePasswordRequest, DeleteAccountRequest)
from app.models.post import Post
from app.models.interaction import PostLike
from app.schemas.user import ActivityResponse
from app.schemas.post import PostResponse
from app.models.comment import Comment
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_reset_token, hash_reset_token,
    generate_verification_token, hash_verification_token,
)
from app.core.config import settings
from app.services.email_service import send_password_reset_email, send_verification_email
import os
import shutil

PASSWORD_RESET_EXPIRE_MINUTES = 15
EMAIL_VERIFICATION_EXPIRE_HOURS = 24


router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def ensure_email_verified_for_login(user: User) -> None:
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="이메일 인증 후 로그인할 수 있습니다")


async def issue_email_verification_token(user: User, db: AsyncSession) -> str:
    await db.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used == False,  # noqa: E712
        )
        .values(used=True)
    )
    plain_token = generate_verification_token()
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_verification_token(plain_token),
            expires_at=datetime.utcnow() + timedelta(hours=EMAIL_VERIFICATION_EXPIRE_HOURS),
        )
    )
    return plain_token


async def deliver_verification_email(user: User, token: str) -> None:
    try:
        await send_verification_email(user.email, user.username, token)
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=503,
            detail="이메일 발송 인증에 실패했습니다. SMTP 설정을 확인해주세요",
        )
    except OSError:
        raise HTTPException(
            status_code=503,
            detail="이메일 발송 서버에 연결할 수 없습니다. SMTP 설정을 확인해주세요",
        )
    except smtplib.SMTPException:
        raise HTTPException(
            status_code=503,
            detail="이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요",
        )


async def deliver_password_reset_email(user: User, token: str) -> None:
    try:
        await send_password_reset_email(user.email, user.username, token)
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=503,
            detail="이메일 발송 인증에 실패했습니다. SMTP 설정을 확인해주세요",
        )
    except OSError:
        raise HTTPException(
            status_code=503,
            detail="이메일 발송 서버에 연결할 수 없습니다. SMTP 설정을 확인해주세요",
        )
    except smtplib.SMTPException:
        raise HTTPException(
            status_code=503,
            detail="이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요",
        )


def password_reset_request_response() -> dict[str, str]:
    return {"message": "비밀번호 찾기 안내를 발송했습니다"}


def ensure_current_password_for_reset(user: User, current_password: str) -> None:
    if not verify_password(current_password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 현재 비밀번호가 틀렸습니다")

# ── 현재 유저 가져오기
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
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

    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 사용중인 닉네임입니다")

    new_user = User(
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        email_verified=False,

    )
    db.add(new_user)
    try:
        await db.flush()
        plain_token = await issue_email_verification_token(new_user, db)
        await deliver_verification_email(new_user, plain_token)
        await db.commit()
    except HTTPException:
        await db.rollback()
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="이미 사용중인 이메일 또는 닉네임입니다")
    await db.refresh(new_user)
    return new_user


@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    message = "가입된 이메일이라면 인증 메일을 발송했습니다"
    if not user or user.email_verified:
        return {"message": message}

    plain_token = await issue_email_verification_token(user, db)
    await deliver_verification_email(user, plain_token)
    await db.commit()
    return {"message": message}


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    token_hash = hash_verification_token(token)
    result = await db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.used == False,  # noqa: E712
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        raise HTTPException(status_code=400, detail="유효하지 않은 인증 링크입니다")
    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="만료된 인증 링크입니다")

    user_result = await db.execute(select(User).where(User.id == verification.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    verification.used = True
    await db.commit()
    return {"message": "이메일 인증이 완료되었습니다"}

# ── 2. 로그인
@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")
    ensure_email_verified_for_login(user)
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

# ── 6. 비밀번호 찾기 (재설정 토큰 발급)
@router.post("/find-password")
async def find_password(data: FindPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # User Enumeration 방지: 이메일 존재 여부와 무관하게 동일한 메시지 반환
    if not user:
        return password_reset_request_response()

    # 기존 미사용 토큰 전부 무효화 (토큰 재발급 시 이전 토큰 차단)
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,  # noqa: E712
        )
        .values(used=True)
    )

    # 새 토큰 생성 — 평문은 클라이언트에만, 해시만 DB에 저장
    plain_token = generate_reset_token()
    reset_record = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_reset_token(plain_token),
        expires_at=datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES),
    )
    db.add(reset_record)
    try:
        await deliver_password_reset_email(user, plain_token)
        await db.commit()
    except HTTPException:
        await db.rollback()
        raise

    return password_reset_request_response()


# ── 7. 비밀번호 재설정 (토큰 검증 후 변경)
@router.patch("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # 1) 토큰 해시로 DB 조회
    token_hash = hash_reset_token(data.token)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False,  # noqa: E712
        )
    )
    reset_record = result.scalar_one_or_none()

    if not reset_record:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다")

    # 2) 만료 시간 검증
    if reset_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail=f"만료된 토큰입니다 ({PASSWORD_RESET_EXPIRE_MINUTES}분 이내에 사용해야 합니다)",
        )

    # 3) 유저 조회 및 비밀번호 변경
    user_result = await db.execute(select(User).where(User.id == reset_record.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    user.password = hash_password(data.new_password)

    # 4) 토큰 사용 처리 (재사용 방지)
    reset_record.used = True

    await db.commit()
    return {"message": "비밀번호가 재설정되었습니다"}


@router.patch("/reset-password/current")
async def reset_password_with_current(
    data: ResetPasswordWithCurrentRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 현재 비밀번호가 틀렸습니다")

    ensure_current_password_for_reset(user, data.current_password)
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
    if data.username is not None:
        current_user.username = data.username
    if data.bio is not None:
        current_user.bio = data.bio
    await db.commit()
    await db.refresh(current_user)
    return current_user

# ── 10. 프로필 이미지 업로드
@router.post("/profile/image", response_model=UserResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    os.makedirs("uploads/profile", exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    file_path = f"uploads/profile/{current_user.id}{ext}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    current_user.profile_image = file_path
    await db.commit()
    await db.refresh(current_user)
    return current_user

# ── 10-1. 비밀번호 변경 (로그인 상태)
@router.patch("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.password):
        raise HTTPException(status_code=401, detail="현재 비밀번호가 틀렸습니다")
    current_user.password = hash_password(data.new_password)
    await db.commit()
    return {"message": "비밀번호가 변경되었습니다"}

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
    if admin_secret != settings.ADMIN_SECRET:
        if admin_secret != os.getenv("ADMIN_SECRET", "admin_secret_change_me"):
            raise HTTPException(status_code=403, detail="관리자 코드가 틀렸습니다.")
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 사용중인 이메일입니다")
    new_user = User(
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        role="admin",
        email_verified=True,
        email_verified_at=datetime.utcnow(),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# ── 13. 관리자 승격
@router.patch("/promote/admin")
async def promote_to_admin(email: str, admin_secret: str, db: AsyncSession = Depends(get_db)):
    if admin_secret != settings.ADMIN_SECRET:
        if admin_secret != os.getenv("ADMIN_SECRET", "admin_secret_change_me"):
            raise HTTPException(status_code=403, detail="관리자 코드가 틀렸습니다.")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    user.role = "admin"
    await db.commit()
    return {"message": f"{email} 계정이 관리자로 승격되었습니다."}

# 14. 프로필 조회
@router.get("/profile/{user_id}")
async def get_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user


# ── 15. 활동 내역 조회
@router.get("/activity", response_model=ActivityResponse)
async def get_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    posts_result = await db.execute(
        select(Post)
        .where(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
    )
    posts = posts_result.scalars().all()

    comments_result = await db.execute(
        select(Comment)
        .where(Comment.user_id == current_user.id)
        .order_by(Comment.created_at.desc())
    )
    comments = comments_result.scalars().all()

    return {"posts": posts, "comments": comments}

# ── 16. 좋아요 목록 조회
@router.get("/likes", response_model=list[PostResponse])
async def get_likes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Post)
        .join(PostLike, Post.id == PostLike.post_id)
        .where(PostLike.user_id == current_user.id)
        .order_by(PostLike.created_at.desc())
    )
    return result.scalars().all()
