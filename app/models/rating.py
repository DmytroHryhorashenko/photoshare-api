from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.photo import Photo
    from app.models.user import User


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("photo_id", "user_id", name="uq_ratings_photo_user"),
        CheckConstraint("value >= 1 AND value <= 5", name="ck_ratings_value_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    photo: Mapped["Photo"] = relationship(back_populates="ratings")
    user: Mapped["User"] = relationship(back_populates="ratings")

    def __repr__(self) -> str:
        return (
            f"<Rating id={self.id} photo_id={self.photo_id} "
            f"user_id={self.user_id} value={self.value}>"
        )
