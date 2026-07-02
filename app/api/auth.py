"""Authentication API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, decode_access_token
from app.dependencies import get_current_active_user, get_db, oauth2_scheme
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.services.auth import authenticate_user, logout_user, register_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await register_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(db, credentials.email, credentials.password)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
    )
    return Token(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    del current_user
    payload = decode_access_token(token)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    await logout_user(db, token, expires_at)
