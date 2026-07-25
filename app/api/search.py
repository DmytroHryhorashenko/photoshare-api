"""Search API routes."""

from datetime import datetime

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


@router.get(
    "/search",
    response_model=list[PhotoResponse],
    summary="Search and filter photos",
    description=(
        "Filter by keyword, tag, minimum rating, or upload date range. "
        "Sort by date or rating. The user_id filter requires moderator or admin role."
    ),
    responses={
        200: {"description": "Matching photos"},
        400: {"description": "Invalid sort_by, order, tag, or date range"},
        403: {"description": "user_id filter used without sufficient permissions"},
    },
)
async def search_photos(
    keyword: str | None = None,
    tag: str | None = None,
    min_rating: float | None = Query(default=None, ge=1, le=5),
    sort_by: str = "date",
    order: str = "desc",
    user_id: int | None = None,
    date_from: datetime | None = Query(
        default=None,
        description="Include photos created at or after this UTC datetime",
    ),
    date_to: datetime | None = Query(
        default=None,
        description="Include photos created at or before this UTC datetime",
    ),
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

    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be less than or equal to date_to",
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
        date_from=date_from,
        date_to=date_to,
    )
    return photos
