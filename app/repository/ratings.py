from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rating import Rating


async def create_rating(
    db: AsyncSession,
    *,
    photo_id: int,
    user_id: int,
    value: int,
) -> Rating:
    rating = Rating(
        photo_id=photo_id,
        user_id=user_id,
        value=value,
    )
    db.add(rating)
    await db.flush()
    await db.refresh(rating)
    return rating


async def get_rating_by_id(db: AsyncSession, rating_id: int) -> Rating | None:
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    return result.scalar_one_or_none()


async def get_user_rating_for_photo(
    db: AsyncSession,
    photo_id: int,
    user_id: int,
) -> Rating | None:
    result = await db.execute(
        select(Rating).where(
            Rating.photo_id == photo_id,
            Rating.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_photo_ratings(db: AsyncSession, photo_id: int) -> list[Rating]:
    result = await db.execute(
        select(Rating)
        .where(Rating.photo_id == photo_id)
        .order_by(Rating.created_at.asc())
    )
    return list(result.scalars().all())


async def get_photo_average_rating(db: AsyncSession, photo_id: int) -> tuple[float, int]:
    result = await db.execute(
        select(func.avg(Rating.value), func.count(Rating.id)).where(
            Rating.photo_id == photo_id
        )
    )
    average, count = result.one()
    return float(average or 0), int(count or 0)


async def delete_rating(db: AsyncSession, rating: Rating) -> None:
    await db.delete(rating)
    await db.flush()
