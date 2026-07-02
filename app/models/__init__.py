"""SQLAlchemy ORM models package.

Import all models here so Alembic can discover metadata automatically.
"""

from app.database import Base
from app.models.comment import Comment
from app.models.photo import Photo
from app.models.rating import Rating
from app.models.tag import Tag, photo_tags
from app.models.token_blacklist import TokenBlacklist
from app.models.transformed_photo import TransformedPhoto
from app.models.user import User, UserRole

__all__ = [
    "Base",
    "Comment",
    "Photo",
    "Rating",
    "Tag",
    "TokenBlacklist",
    "TransformedPhoto",
    "User",
    "UserRole",
    "photo_tags",
]
