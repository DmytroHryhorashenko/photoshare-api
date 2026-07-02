from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin
from app.models.tag import photo_tags

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.rating import Rating
    from app.models.tag import Tag
    from app.models.transformed_photo import TransformedPhoto
    from app.models.user import User


class Photo(TimestampMixin, Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    public_id: Mapped[str] = mapped_column(String(255), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="photos")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=photo_tags,
        back_populates="photos",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="photo",
        cascade="all, delete-orphan",
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="photo",
        cascade="all, delete-orphan",
    )
    transformed_photos: Mapped[list["TransformedPhoto"]] = relationship(
        back_populates="photo",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Photo id={self.id} user_id={self.user_id} public_id={self.public_id!r}>"
