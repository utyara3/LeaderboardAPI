from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from datetime import datetime, timezone, timedelta

from starlette.status import HTTP_401_UNAUTHORIZED

from src.models.refresh_token import RefreshToken
from src.models.user import User

from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    decode_token,
)

from src.config import settings


async def login_token(db: AsyncSession, user: User) -> dict:
    access_token = create_access_token(data={"sub": str(user.id)})
    plain_refresh, hashed_refresh = create_refresh_token()

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    db_token = RefreshToken(
        user_id=user.id, token_hash=hashed_refresh, expires_at=expires_at
    )

    db.add(db_token)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": plain_refresh,
        "token_type": "bearer",
    }


async def refresh_acces_token(db: AsyncSession, refresh_token: str) -> dict:
    res = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.revoked == False)
        .where(RefreshToken.expires_at > datetime.now(timezone.utc))
    )
    tokens = res.scalars().all()

    valid_token = None
    for token in tokens:
        if verify_refresh_token(refresh_token, token.token_hash):
            valid_token = token
            break

    if not valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh_token",
        )

    res = await db.execute(select(User).where(User.id == valid_token.user_id))
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not found")

    valid_token.revoked = True

    new_access_token = create_access_token(data={"sub": user.id})
    new_plain_refresh, new_hashed_refresh = create_refresh_token()

    new_expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    new_db_token = RefreshToken(
        user_id=user.id, token_hash=new_hashed_refresh, expires_at=new_expires_at
    )

    db.add(new_db_token)
    await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_plain_refresh,
        "token_type": "bearer",
    }


async def logout(db: AsyncSession, refresh_token: str) -> bool:
    res = await db.execute(select(RefreshToken).where(RefreshToken.revoked == False))
    tokens = res.scalars().all()

    for token in tokens:
        if verify_refresh_token(refresh_token, token.token_hash):
            token.revoked = True
            await db.commit()
            return True

    return False
