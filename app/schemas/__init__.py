"""Pydantic request/response schemas."""

from app.schemas.auth import Token, TokenPayload, UserLogin, UserRegister
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.photo import (
    PhotoCreate,
    PhotoDetailResponse,
    PhotoResponse,
    PhotoUpdate,
)
from app.schemas.rating import RatingAverageResponse, RatingCreate, RatingResponse
from app.schemas.tag import TagBase, TagResponse
from app.schemas.transformed_photo import TransformRequest, TransformedPhotoResponse
from app.schemas.user import (
    UserBanResponse,
    UserCreate,
    UserPublicProfile,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)

__all__ = [
    "CommentCreate",
    "CommentResponse",
    "CommentUpdate",
    "PhotoCreate",
    "PhotoDetailResponse",
    "PhotoResponse",
    "PhotoUpdate",
    "RatingAverageResponse",
    "RatingCreate",
    "RatingResponse",
    "TagBase",
    "TagResponse",
    "Token",
    "TokenPayload",
    "TransformRequest",
    "TransformedPhotoResponse",
    "UserBanResponse",
    "UserCreate",
    "UserLogin",
    "UserPublicProfile",
    "UserRegister",
    "UserResponse",
    "UserRoleUpdate",
    "UserUpdate",
]
