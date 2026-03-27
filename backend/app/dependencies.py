from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.database import get_db
from app.models.user import User
from app.core.security import decode_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=401, detail="존재하지 않는 유저입니다")
    return user
