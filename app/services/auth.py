from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User, UserRole
from app.repository.users import (
    count_users,
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.auth import UserRegister


async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    result = await db.execute(
        select(TokenBlacklist).where(TokenBlacklist.token == token)
    )
    return result.scalar_one_or_none() is not None


async def blacklist_token(db: AsyncSession, token: str, expires_at: datetime) -> None:
    db.add(TokenBlacklist(token=token, expires_at=expires_at))
    await db.flush()


async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
    if await get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if await get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    role = UserRole.ADMIN if await count_users(db) == 0 else UserRole.USER

    user = await create_user(
        db,
        {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": role,
            "is_active": True,
        },
    )
    await db.commit()
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def logout_user(db: AsyncSession, token: str, expires_at: datetime) -> None:
    if await is_token_blacklisted(db, token):
        return

    await blacklist_token(db, token, expires_at)
    await db.commit()
