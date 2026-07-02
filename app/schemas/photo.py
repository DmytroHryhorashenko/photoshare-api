from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.comment import CommentResponse
from app.schemas.rating import RatingAverageResponse
from app.schemas.tag import TagResponse
from app.schemas.transformed_photo import TransformedPhotoResponse


class PhotoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str | None = Field(default=None, max_length=2000)


class PhotoCreate(PhotoBase):
    tags: list[str] | None = Field(default=None, max_length=5)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        if len(value) > 5:
            raise ValueError("A photo can have at most 5 tags")
        normalized: list[str] = []
        for tag in value:
            cleaned = tag.strip().lower()
            if not cleaned:
                raise ValueError("Tags cannot be empty")
            if len(cleaned) > 100:
                raise ValueError("Each tag must be at most 100 characters")
            normalized.append(cleaned)
        return normalized


class PhotoUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str | None = Field(default=None, max_length=2000)
    tags: list[str] | None = Field(default=None, max_length=5)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        if len(value) > 5:
            raise ValueError("A photo can have at most 5 tags")
        normalized: list[str] = []
        for tag in value:
            cleaned = tag.strip().lower()
            if not cleaned:
                raise ValueError("Tags cannot be empty")
            if len(cleaned) > 100:
                raise ValueError("Each tag must be at most 100 characters")
            normalized.append(cleaned)
        return normalized


class PhotoResponse(PhotoBase):
    id: int
    user_id: int
    image_url: str
    public_id: str
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = Field(default_factory=list)


class PhotoDetailResponse(PhotoResponse):
    comments: list[CommentResponse] = Field(default_factory=list)
    rating_summary: RatingAverageResponse | None = None
    transformed_photos: list[TransformedPhotoResponse] = Field(default_factory=list)
