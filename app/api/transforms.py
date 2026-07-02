"""Transformed photo API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import can_modify_photo
from app.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.repository.photos import (
    create_transformed_photo,
    get_photo_by_id,
    get_photo_transformed_links,
    get_transformed_photo_by_id,
)
from app.schemas.transformed_photo import TransformRequest, TransformedPhotoResponse
from app.services.cloudinary import (
    build_transformation_type,
    build_transformed_url,
    validate_transformation_request,
)
from app.services.qr import generate_qr_code

router = APIRouter()


@router.post(
    "/photos/{photo_id}/transform",
    response_model=TransformedPhotoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_photo_transformation(
    photo_id: int,
    transformation: TransformRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TransformedPhotoResponse:
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

    try:
        validate_transformation_request(transformation)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    transformed_url = build_transformed_url(photo.public_id, transformation)
    qr_code_url = await generate_qr_code(transformed_url)
    transformation_type = build_transformation_type(transformation)

    transformed_photo = await create_transformed_photo(
        db,
        photo_id=photo_id,
        transformation_type=transformation_type,
        transformed_url=transformed_url,
        qr_code_url=qr_code_url,
    )
    await db.commit()
    return transformed_photo


@router.get(
    "/photos/{photo_id}/transforms",
    response_model=list[TransformedPhotoResponse],
)
async def list_photo_transformations(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[TransformedPhotoResponse]:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    return await get_photo_transformed_links(db, photo_id)


@router.get("/transforms/{transform_id}", response_model=TransformedPhotoResponse)
async def get_transformation(
    transform_id: int,
    db: AsyncSession = Depends(get_db),
) -> TransformedPhotoResponse:
    transformed_photo = await get_transformed_photo_by_id(db, transform_id)
    if transformed_photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transformed photo not found",
        )
    return transformed_photo
