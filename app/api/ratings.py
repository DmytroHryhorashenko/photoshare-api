"""Rating API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import can_delete_comment
from app.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.repository.photos import get_photo_by_id
from app.repository.ratings import (
    create_rating,
    delete_rating,
    get_photo_average_rating,
    get_rating_by_id,
    get_user_rating_for_photo,
)
from app.schemas.rating import RatingAverageResponse, RatingCreate, RatingResponse

router = APIRouter()


@router.post(
    "/photos/{photo_id}/ratings",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def rate_photo(
    photo_id: int,
    rating_data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RatingResponse:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    if photo.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate your own photo",
        )

    existing_rating = await get_user_rating_for_photo(db, photo_id, current_user.id)
    if existing_rating is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this photo",
        )

    rating = await create_rating(
        db,
        photo_id=photo_id,
        user_id=current_user.id,
        value=rating_data.value,
    )
    await db.commit()
    return rating


@router.get("/photos/{photo_id}/ratings", response_model=RatingAverageResponse)
async def get_photo_rating_summary(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
) -> RatingAverageResponse:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    average_rating, ratings_count = await get_photo_average_rating(db, photo_id)
    return RatingAverageResponse(
        photo_id=photo_id,
        average_rating=average_rating,
        ratings_count=ratings_count,
    )


@router.delete("/ratings/{rating_id}")
async def delete_photo_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    rating = await get_rating_by_id(db, rating_id)
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
        )

    if not can_delete_comment(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    await delete_rating(db, rating)
    await db.commit()
    return {"message": "Rating deleted successfully"}
