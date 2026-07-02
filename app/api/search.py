"""Search API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_optional_current_user
from app.models.user import User, UserRole
from app.repository.photos import search_photos as search_photos_repository
from app.schemas.photo import PhotoResponse
from app.utils.tags import normalize_tag_name

router = APIRouter()

ALLOWED_SORT_BY = {"date", "rating"}
ALLOWED_ORDER = {"asc", "desc"}


@router.get("/search", response_model=list[PhotoResponse])
async def search_photos(
    keyword: str | None = None,
    tag: str | None = None,
    min_rating: float | None = Query(default=None, ge=1, le=5),
    sort_by: str = "date",
    order: str = "desc",
    user_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> list[PhotoResponse]:
    if sort_by not in ALLOWED_SORT_BY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be 'date' or 'rating'",
        )

    if order not in ALLOWED_ORDER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order must be 'asc' or 'desc'",
        )

    normalized_tag: str | None = None
    if tag is not None:
        try:
            normalized_tag = normalize_tag_name(tag)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    if user_id is not None:
        if current_user is None or current_user.role not in {
            UserRole.MODERATOR,
            UserRole.ADMIN,
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    photos = await search_photos_repository(
        db,
        keyword=keyword,
        tag=normalized_tag,
        min_rating=min_rating,
        sort_by=sort_by,
        order=order,
        user_id=user_id,
    )
    return photos
