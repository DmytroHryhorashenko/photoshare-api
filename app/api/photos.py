"""Photo API routes."""

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import can_modify_photo
from app.dependencies import get_current_active_user, get_db
from app.models.photo import Photo
from app.models.user import User
from app.repository.photos import (
    attach_tags_to_photo,
    create_photo,
    delete_photo,
    get_or_create_tags,
    get_photo_by_id,
    get_photo_detail,
    update_photo,
)
from app.schemas.photo import PhotoDetailResponse, PhotoResponse, PhotoUpdate
from app.schemas.rating import RatingAverageResponse
from app.services.cloudinary import delete_photo as delete_cloudinary_photo
from app.services.cloudinary import upload_photo
from app.utils.tags import normalize_tag_names

router = APIRouter()

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
}


def validate_image_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed (jpeg, png, gif, webp)",
        )


def build_photo_detail_response(photo: Photo) -> PhotoDetailResponse:
    rating_summary = None
    if photo.ratings:
        rating_summary = RatingAverageResponse(
            photo_id=photo.id,
            average_rating=sum(rating.value for rating in photo.ratings) / len(photo.ratings),
            ratings_count=len(photo.ratings),
        )

    base = PhotoResponse.model_validate(photo)
    return PhotoDetailResponse(
        **base.model_dump(),
        comments=photo.comments,
        rating_summary=rating_summary,
        transformed_photos=photo.transformed_photos,
    )


@router.post(
    "",
    response_model=PhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a photo",
    description="Upload an image file with optional description and up to 5 tags.",
    responses={
        201: {"description": "Photo uploaded"},
        400: {"description": "Invalid file type or too many tags"},
        500: {"description": "Cloudinary or database failure"},
    },
)
async def upload_user_photo(
    file: UploadFile = File(...),
    description: str | None = Form(default=None),
    tags: list[str] | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Photo:
    validate_image_file(file)

    try:
        normalized_tags = normalize_tag_names(tags)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    upload_result: dict[str, str] | None = None
    try:
        upload_result = await upload_photo(file)
        photo = await create_photo(
            db,
            user_id=current_user.id,
            description=description,
            image_url=upload_result["image_url"],
            public_id=upload_result["public_id"],
        )

        if normalized_tags:
            tag_models = await get_or_create_tags(db, normalized_tags)
            photo = await attach_tags_to_photo(db, photo, tag_models)

        await db.commit()
        await db.refresh(photo, attribute_names=["tags"])
        return photo
    except HTTPException:
        await db.rollback()
        if upload_result is not None:
            await delete_cloudinary_photo(upload_result["public_id"])
        raise
    except Exception as exc:
        await db.rollback()
        if upload_result is not None:
            await delete_cloudinary_photo(upload_result["public_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create photo",
        ) from exc


@router.get(
    "/{photo_id}",
    response_model=PhotoDetailResponse,
    summary="Get photo details",
    description="Returns photo metadata, tags, comments, rating summary, and transformations.",
    responses={404: {"description": "Photo not found"}},
)
async def get_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
) -> PhotoDetailResponse:
    photo = await get_photo_detail(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    return build_photo_detail_response(photo)


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_user_photo(
    photo_id: int,
    update_data: PhotoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Photo:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    if not can_modify_photo(photo.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    data = update_data.model_dump(exclude_unset=True)
    tag_names = data.pop("tags", None)

    if data:
        photo = await update_photo(db, photo, data)

    if tag_names is not None:
        try:
            normalized_tags = normalize_tag_names(tag_names)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        tag_models = await get_or_create_tags(db, normalized_tags)
        photo = await attach_tags_to_photo(db, photo, tag_models)

    await db.commit()
    await db.refresh(photo, attribute_names=["tags"])
    return photo


@router.delete("/{photo_id}")
async def delete_user_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    if not can_modify_photo(photo.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    public_id = photo.public_id
    await delete_cloudinary_photo(public_id)
    await delete_photo(db, photo)
    await db.commit()
    return {"message": "Photo deleted successfully"}
