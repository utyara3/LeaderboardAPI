from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select

from src.database import AsyncSession, get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserLogin, UserResponse
from src.auth.utils import hash_password, verify_password, create_access_token
from src.auth.dependencies import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> dict:
    user_email = user_data.email
    username = user_data.username
    user_password = user_data.password

    res = await db.execute(select(User).where(User.email == user_email))
    is_user_exists = res.scalar_one_or_none()

    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this email is already_exists",
        )

    res = await db.execute(select(User).where(User.username == username))
    is_user_exists = res.scalar_one_or_none()

    if is_user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this username is already_exists",
        )

    hashed_password = hash_password(user_password)

    new_user = User(
        username=username, email=user_email, hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})

    # Сделать TokenResponse
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(new_user),
    }


@auth_router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict:
    username = form_data.username
    user_password = form_data.password

    res = await db.execute(select(User).where(User.username == username))
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    is_password_correct = verify_password(user_password, user.hashed_password)

    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password is incorrect"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "user": UserResponse.model_validate(user)}


@auth_router.get("/me")
async def get_me(
    current_user: AsyncSession = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
