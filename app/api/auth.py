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
    summary="Register a new user",
    description="Create an account. The first registered user receives the admin role.",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Email or username already taken"},
    },
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await register_user(db, user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and obtain JWT",
    description="Authenticate with email and password. Returns a Bearer access token.",
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid credentials or inactive account"},
    },
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(db, credentials.email, credentials.password)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
    )
    return Token(access_token=access_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and invalidate token",
    description="Adds the current JWT to the server-side blacklist until it expires.",
    responses={204: {"description": "Token blacklisted successfully"}},
)
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_active_user),
) -> None:
    payload = decode_access_token(token)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    await logout_user(db, token, expires_at)
