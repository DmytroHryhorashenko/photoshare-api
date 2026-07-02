"""User API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_admin
from app.core.security import hash_password
from app.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.repository.users import (
    count_user_photos,
    get_user_by_email,
    get_user_by_username,
    set_user_active_status,
    set_user_role,
    update_user,
)
from app.schemas.user import (
    UserBanResponse,
    UserPublicProfile,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    responses={
        200: {"description": "Profile updated"},
        400: {"description": "Duplicate email/username or empty update"},
    },
)
async def update_me(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    data = update_data.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    if "email" in data and data["email"] != current_user.email:
        existing = await get_user_by_email(db, data["email"])
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if "username" in data and data["username"] != current_user.username:
        existing = await get_user_by_username(db, data["username"])
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))

    user = await update_user(db, current_user, data)
    await db.commit()
    return user


@router.get(
    "/{username}",
    response_model=UserPublicProfile,
    summary="Get public user profile",
    responses={404: {"description": "User not found"}},
)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> UserPublicProfile:
    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    photos_count = await count_user_photos(db, user.id)
    return UserPublicProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        uploaded_photos_count=photos_count,
    )


@router.patch("/{user_id}/ban", response_model=UserBanResponse)
async def ban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserBanResponse:
    user = await set_user_active_status(db, user_id, is_active=False)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.commit()
    return UserBanResponse(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        message="User has been banned",
    )


@router.patch("/{user_id}/unban", response_model=UserBanResponse)
async def unban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserBanResponse:
    user = await set_user_active_status(db, user_id, is_active=True)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.commit()
    return UserBanResponse(
        id=user.id,
        username=user.username,
        is_active=user.is_active,
        message="User has been unbanned",
    )


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    user = await set_user_role(db, user_id, role_data.role)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.commit()
    return user
