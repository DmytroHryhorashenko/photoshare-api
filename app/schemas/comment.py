from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_comment_text(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Comment text cannot be empty")
    return cleaned


class CommentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _strip_comment_text(value)


class CommentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _strip_comment_text(value)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_id: int
    user_id: int
    text: str
    created_at: datetime
    updated_at: datetime
