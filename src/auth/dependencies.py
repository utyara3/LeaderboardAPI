from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select

from src.database import AsyncSession, get_db
from src.models.user import User
from src.auth.utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid."
        )

    user_id = payload["sub"]

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return user
