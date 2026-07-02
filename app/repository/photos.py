from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.photo import Photo
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.transformed_photo import TransformedPhoto


async def create_photo(
    db: AsyncSession,
    *,
    user_id: int,
    description: str | None,
    image_url: str,
    public_id: str,
) -> Photo:
    photo = Photo(
        user_id=user_id,
        description=description,
        image_url=image_url,
        public_id=public_id,
    )
    db.add(photo)
    await db.flush()
    await db.refresh(photo)
    return photo


async def get_photo_by_id(db: AsyncSession, photo_id: int) -> Photo | None:
    result = await db.execute(
        select(Photo)
        .where(Photo.id == photo_id)
        .options(selectinload(Photo.tags))
    )
    return result.scalar_one_or_none()


async def get_user_photo_by_id(
    db: AsyncSession,
    photo_id: int,
    user_id: int,
) -> Photo | None:
    result = await db.execute(
        select(Photo)
        .where(Photo.id == photo_id, Photo.user_id == user_id)
        .options(selectinload(Photo.tags))
    )
    return result.scalar_one_or_none()


async def update_photo(
    db: AsyncSession,
    photo: Photo,
    update_data: dict,
) -> Photo:
    for field, value in update_data.items():
        setattr(photo, field, value)
    await db.flush()
    await db.refresh(photo, attribute_names=["tags"])
    return photo


async def delete_photo(db: AsyncSession, photo: Photo) -> None:
    await db.delete(photo)
    await db.flush()


async def get_photo_detail(db: AsyncSession, photo_id: int) -> Photo | None:
    result = await db.execute(
        select(Photo)
        .where(Photo.id == photo_id)
        .options(
            selectinload(Photo.tags),
            selectinload(Photo.comments),
            selectinload(Photo.ratings),
            selectinload(Photo.transformed_photos),
        )
    )
    return result.scalar_one_or_none()


async def get_or_create_tags(db: AsyncSession, tag_names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    for name in tag_names:
        result = await db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            await db.flush()
        tags.append(tag)
    return tags


async def attach_tags_to_photo(
    db: AsyncSession,
    photo: Photo,
    tags: list[Tag],
) -> Photo:
    photo.tags = tags
    await db.flush()
    await db.refresh(photo, attribute_names=["tags"])
    return photo


async def create_transformed_photo(
    db: AsyncSession,
    *,
    photo_id: int,
    transformation_type: str,
    transformed_url: str,
    qr_code_url: str,
) -> TransformedPhoto:
    transformed_photo = TransformedPhoto(
        photo_id=photo_id,
        transformation_type=transformation_type,
        transformed_url=transformed_url,
        qr_code_url=qr_code_url,
    )
    db.add(transformed_photo)
    await db.flush()
    await db.refresh(transformed_photo)
    return transformed_photo


async def get_transformed_photo_by_id(
    db: AsyncSession,
    transform_id: int,
) -> TransformedPhoto | None:
    result = await db.execute(
        select(TransformedPhoto).where(TransformedPhoto.id == transform_id)
    )
    return result.scalar_one_or_none()


async def get_photo_transformed_links(
    db: AsyncSession,
    photo_id: int,
) -> list[TransformedPhoto]:
    result = await db.execute(
        select(TransformedPhoto)
        .where(TransformedPhoto.photo_id == photo_id)
        .order_by(TransformedPhoto.created_at.asc())
    )
    return list(result.scalars().all())


async def search_photos(
    db: AsyncSession,
    *,
    keyword: str | None = None,
    tag: str | None = None,
    min_rating: float | None = None,
    sort_by: str = "date",
    order: str = "desc",
    user_id: int | None = None,
) -> list[Photo]:
    rating_stats = (
        select(
            Rating.photo_id.label("photo_id"),
            func.avg(Rating.value).label("avg_rating"),
        )
        .group_by(Rating.photo_id)
        .subquery()
    )

    stmt = select(Photo).options(selectinload(Photo.tags))

    if keyword:
        stmt = stmt.where(Photo.description.ilike(f"%{keyword}%"))

    if user_id is not None:
        stmt = stmt.where(Photo.user_id == user_id)

    if tag:
        stmt = stmt.join(Photo.tags).where(Tag.name == tag)

    needs_rating_join = min_rating is not None or sort_by == "rating"
    if needs_rating_join:
        stmt = stmt.outerjoin(rating_stats, Photo.id == rating_stats.c.photo_id)
        if min_rating is not None:
            stmt = stmt.where(func.coalesce(rating_stats.c.avg_rating, 0) >= min_rating)

    if sort_by == "rating":
        sort_column = func.coalesce(rating_stats.c.avg_rating, 0)
    else:
        sort_column = Photo.created_at

    if order == "asc":
        stmt = stmt.order_by(sort_column.asc())
    else:
        stmt = stmt.order_by(sort_column.desc())

    result = await db.execute(stmt)
    return list(result.scalars().unique().all())
