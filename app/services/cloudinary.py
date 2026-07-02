"""Cloudinary media upload, deletion, and transformation URL building."""

import asyncio

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.schemas.transformed_photo import ImageFormat, TransformRequest


def _configure_cloudinary() -> None:
    if not all(
        [
            settings.cloudinary_name,
            settings.cloudinary_api_key,
            settings.cloudinary_api_secret,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary is not configured",
        )

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def build_transformation_options(transformation: TransformRequest) -> dict:
    options: dict = {}

    if transformation.width is not None:
        options["width"] = transformation.width
    if transformation.height is not None:
        options["height"] = transformation.height
    if transformation.crop is not None:
        options["crop"] = transformation.crop.value
    if transformation.angle is not None:
        options["angle"] = transformation.angle
    if transformation.effect is not None:
        options["effect"] = transformation.effect
    if transformation.format is not None and transformation.format != ImageFormat.AUTO:
        options["format"] = transformation.format.value

    return options


def build_transformation_type(transformation: TransformRequest) -> str:
    parts: list[str] = []
    if transformation.width is not None:
        parts.append(f"w{transformation.width}")
    if transformation.height is not None:
        parts.append(f"h{transformation.height}")
    if transformation.crop is not None:
        parts.append(f"c_{transformation.crop.value}")
    if transformation.angle is not None:
        parts.append(f"a_{transformation.angle}")
    if transformation.effect is not None:
        parts.append(f"e_{transformation.effect}")
    if transformation.format is not None:
        parts.append(f"f_{transformation.format.value}")
    return "_".join(parts)


def validate_transformation_request(transformation: TransformRequest) -> None:
    if not build_transformation_options(transformation):
        raise ValueError("At least one transformation option is required")


def build_transformed_url(public_id: str, transformation: TransformRequest) -> str:
    _configure_cloudinary()
    validate_transformation_request(transformation)

    options = build_transformation_options(transformation)
    url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        secure=True,
        **options,
    )
    return url


async def upload_photo(file: UploadFile) -> dict[str, str]:
    _configure_cloudinary()
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            contents,
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image to Cloudinary",
        ) from exc

    return {
        "image_url": result["secure_url"],
        "public_id": result["public_id"],
    }


async def upload_image_bytes(
    image_bytes: bytes,
    *,
    folder: str,
    public_id_prefix: str,
) -> str:
    _configure_cloudinary()

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            image_bytes,
            resource_type="image",
            folder=folder,
            public_id=public_id_prefix,
            overwrite=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image to Cloudinary",
        ) from exc

    return result["secure_url"]


async def delete_photo(public_id: str) -> None:
    _configure_cloudinary()

    try:
        await asyncio.to_thread(
            cloudinary.uploader.destroy,
            public_id,
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image from Cloudinary",
        ) from exc
