import hashlib
import secrets
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings

_BCRYPT_ROUNDS = 12
_BCRYPT_MAX_BYTES = 72


def _bcrypt_password_bytes(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if len(encoded) <= _BCRYPT_MAX_BYTES:
        return encoded
    return hashlib.sha256(encoded).hexdigest().encode("ascii")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        _bcrypt_password_bytes(password),
        bcrypt.gensalt(rounds=_BCRYPT_ROUNDS),
    ).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_bcrypt_password_bytes(plain), hashed.encode("utf-8"))
    except (TypeError, ValueError):
        return False
                                                                                                
def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)       
    return jwt.encode({**data, "exp": expire, "type": "access"}, settings.SECRET_KEY,          
settings.ALGORITHM)                                                                            
                                                                                                
def create_refresh_token(data: dict) -> str:                                                   
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({**data, "exp": expire, "type": "refresh"}, settings.SECRET_KEY,
settings.ALGORITHM)                                                                            

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def generate_reset_token() -> str:
    """암호학적으로 안전한 평문 토큰 생성 (클라이언트에게 전달하는 값)"""
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    """토큰을 SHA-256으로 해싱 (DB 저장용)"""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_verification_token() -> str:
    """이메일 인증용 암호학적 토큰 생성."""
    return secrets.token_urlsafe(32)


def hash_verification_token(token: str) -> str:
    """이메일 인증 토큰을 DB 저장용 SHA-256 해시로 변환."""
    return hashlib.sha256(token.encode()).hexdigest()
