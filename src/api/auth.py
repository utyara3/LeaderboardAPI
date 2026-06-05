from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select

from src.core.database import AsyncSession, get_db

from src.models.user import User
from src.models.refresh_token import RefreshToken

from src.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse

from src.services.auth_service import login_token, refresh_acces_token, logout

from src.auth.utils import (
    create_refresh_token,
    hash_password,
    verify_password,
    create_access_token,
)
from src.auth.dependencies import get_current_user


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    user_email = user_data.email
    username = user_data.username
    user_password = user_data.password

    res = await db.execute(select(User).where(User.email == user_email))
    is_user_exists = res.scalar_one_or_none()

    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this email is already exists",
        )

    res = await db.execute(select(User).where(User.username == username))
    is_user_exists = res.scalar_one_or_none()

    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this username is already exists",
        )

    hashed_password = hash_password(user_password)

    new_user = User(
        username=username, email=user_email, hashed_password=hashed_password
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    tokens = await login_token(db=db, user=new_user)

    response = {
        **tokens,
        "user": UserResponse.model_validate(new_user),
    }

    return TokenResponse.model_validate(response)


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    username = form_data.username
    user_password = form_data.password

    res = await db.execute(select(User).where(User.username == username))
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentails"
        )

    is_password_correct = verify_password(user_password, user.hashed_password)

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentails"
        )

    tokens = await login_token(db=db, user=user)
    response = {**tokens, "user": UserResponse.model_validate(user)}

    return TokenResponse.model_validate(response)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    token = await refresh_acces_token(db=db, refresh_token=refresh_token)

    return TokenResponse.model_validate(token)


@auth_router.post("/logout")
async def logout_route(refresh_token: str, db: AsyncSession = Depends(get_db)) -> dict:
    success = await logout(db=db, refresh_token=refresh_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    return {"message": "Logged out successfully"}


@auth_router.get("/me")
async def get_me(
    current_user: AsyncSession = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
