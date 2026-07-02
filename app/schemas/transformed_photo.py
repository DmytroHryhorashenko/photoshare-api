from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CropMode(str, Enum):
    SCALE = "scale"
    FIT = "fit"
    FILL = "fill"
    CROP = "crop"
    THUMB = "thumb"
    PAD = "pad"
    LIMIT = "limit"


class ImageFormat(str, Enum):
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    AUTO = "auto"


class TransformRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    width: int | None = Field(default=None, gt=0, le=10000)
    height: int | None = Field(default=None, gt=0, le=10000)
    crop: CropMode | None = None
    angle: int | None = Field(default=None, ge=-360, le=360)
    effect: str | None = Field(default=None, max_length=100)
    format: ImageFormat | None = None

    @field_validator("effect")
    @classmethod
    def validate_effect(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed_effects = {
            "grayscale",
            "sepia",
            "blur",
            "sharpen",
            "pixelate",
            "oil_paint",
            "cartoonify",
        }
        normalized = value.strip().lower()
        if normalized not in allowed_effects:
            allowed = ", ".join(sorted(allowed_effects))
            raise ValueError(f"effect must be one of: {allowed}")
        return normalized


class TransformedPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_id: int
    transformation_type: str
    transformed_url: str
    qr_code_url: str | None = None
    created_at: datetime
