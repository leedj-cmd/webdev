from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    email_verified: bool
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class FindIdRequest(BaseModel):
    username: str

class FindPasswordRequest(BaseModel):
    email: EmailStr

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str          # /find-password에서 발급받은 재설정 토큰
    new_password: str

class ResetPasswordWithCurrentRequest(BaseModel):
    email: EmailStr
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class DeleteAccountRequest(BaseModel):
    password: str

from app.schemas.post import PostResponse
from app.schemas.comment import CommentResponse

class ActivityResponse(BaseModel):
    posts: list[PostResponse]
    comments: list[CommentResponse]

class UserProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    email_verified: bool
    is_suspended: bool
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
