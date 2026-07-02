from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import Photo
from app.models.user import User, UserRole


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def count_users(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def count_user_photos(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count()).select_from(Photo).where(Photo.user_id == user_id)
    )
    return result.scalar_one()


async def create_user(db: AsyncSession, user_data: dict) -> User:
    user = User(**user_data)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


async def set_user_active_status(
    db: AsyncSession,
    user_id: int,
    is_active: bool,
) -> User | None:
    user = await get_user_by_id(db, user_id)
    if user is None:
        return None
    user.is_active = is_active
    await db.flush()
    await db.refresh(user)
    return user


async def set_user_role(
    db: AsyncSession,
    user_id: int,
    role: UserRole,
) -> User | None:
    user = await get_user_by_id(db, user_id)
    if user is None:
        return None
    user.role = role
    await db.flush()
    await db.refresh(user)
    return user
