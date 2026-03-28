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
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# 아이디 찾기
class FindIdRequest(BaseModel):
    username: str

# 비밀번호 찾기
class FindPasswordRequest(BaseModel):
    email: EmailStr

# 비밀번호 재설정
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

# 프로필 수정
class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None

# 회원 탈퇴
class DeleteAccountRequest(BaseModel):
    password: str