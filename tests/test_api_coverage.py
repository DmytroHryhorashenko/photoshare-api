"""Additional API route coverage tests."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.models.comment import Comment
from app.models.photo import Photo
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.token_blacklist import TokenBlacklist
from app.models.transformed_photo import TransformedPhoto
from app.models.user import User, UserRole
from tests.helpers import (
    auth_header,
    create_photo_in_db,
    login_user,
    make_jpeg_bytes,
    promote_to_admin,
    register_user,
)


@pytest.mark.asyncio
async def test_update_photo_tags_only(client, db_session):
    user = await register_user(client, "tags_only", "tags_only@example.com")
    token = await login_user(client, "tags_only@example.com")
    photo = await create_photo_in_db(db_session, user["id"], public_id="tags-only-photo")
    await db_session.commit()

    response = await client.put(
        f"/api/v1/photos/{photo.id}",
        headers=auth_header(token),
        json={"tags": ["sunset", "beach"]},
    )
    assert response.status_code == 200
    assert len(response.json()["tags"]) == 2


@pytest.mark.asyncio
async def test_get_photo_detail_with_ratings_and_comments(client, db_session):
    owner = await register_user(client, "detail_owner2", "detail_owner2@example.com")
    commenter = await register_user(client, "detail_commenter", "detail_commenter@example.com")
    owner_token = await login_user(client, "detail_owner2@example.com")
    commenter_token = await login_user(client, "detail_commenter@example.com")
    photo = await create_photo_in_db(db_session, owner["id"], public_id="detail-rich-photo")
    await db_session.commit()

    await client.post(
        f"/api/v1/photos/{photo.id}/comments",
        headers=auth_header(commenter_token),
        json={"text": "Nice shot"},
    )
    await client.post(
        f"/api/v1/photos/{photo.id}/ratings",
        headers=auth_header(commenter_token),
        json={"value": 5},
    )

    response = await client.get(f"/api/v1/photos/{photo.id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["comments"]) == 1
    assert body["rating_summary"]["average_rating"] == 5.0


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
@patch("app.api.photos.upload_photo", new_callable=AsyncMock)
async def test_upload_photo_reraises_http_exception(mock_upload, mock_delete, client):
    mock_upload.side_effect = HTTPException(status_code=400, detail="Bad upload")
    await register_user(client, "upload_http", "upload_http@example.com")
    token = await login_user(client, "upload_http@example.com")

    response = await client.post(
        "/api/v1/photos",
        headers=auth_header(token),
        files=[("file", ("photo.jpg", make_jpeg_bytes(), "image/jpeg"))],
    )
    assert response.status_code == 400
    mock_delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_delete_other_users_photo(client, db_session):
    owner = await register_user(client, "del_owner_admin2", "del_owner_admin2@example.com")
    admin = await register_user(client, "del_admin2", "del_admin2@example.com")
    await promote_to_admin(db_session, admin["id"])
    admin_token = await login_user(client, "del_admin2@example.com")
    photo = await create_photo_in_db(db_session, owner["id"], public_id="admin-delete-photo")
    await db_session.commit()

    with patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock):
        response = await client.delete(
            f"/api/v1/photos/{photo.id}",
            headers=auth_header(admin_token),
        )
    assert response.status_code == 200


def test_model_repr_strings():
    assert "Photo" in repr(
        Photo(
            id=1,
            user_id=1,
            description="d",
            image_url="u",
            public_id="p",
        )
    )
    assert "User" in repr(
        User(
            id=1,
            username="u",
            email="e@example.com",
            password_hash="h",
            role=UserRole.USER,
            is_active=True,
        )
    )
    assert "Comment" in repr(Comment(id=1, photo_id=1, user_id=1, text="t"))
    assert "Rating" in repr(Rating(id=1, photo_id=1, user_id=1, value=5))
    assert "Tag" in repr(Tag(id=1, name="nature"))
    assert "TokenBlacklist" in repr(
        TokenBlacklist(
            id=1,
            token="tok",
            expires_at=datetime.now(timezone.utc),
        )
    )
    assert "TransformedPhoto" in repr(
        TransformedPhoto(
            id=1,
            photo_id=1,
            transformation_type="w100",
            transformed_url="https://example.com/t.jpg",
            qr_code_url="https://example.com/qr.png",
        )
    )


@pytest.mark.asyncio
async def test_build_photo_detail_response_with_ratings():
    from app.api.photos import build_photo_detail_response
    from app.models.photo import Photo
    from app.models.rating import Rating

    now = datetime.now(timezone.utc)
    photo = Photo(
        id=1,
        user_id=1,
        description="Rated",
        image_url="https://example.com/p.jpg",
        public_id="rated-photo",
        created_at=now,
        updated_at=now,
    )
    photo.ratings = [
        Rating(id=1, photo_id=1, user_id=2, value=4),
        Rating(id=2, photo_id=1, user_id=3, value=2),
    ]
    photo.comments = []
    photo.transformed_photos = []
    photo.tags = []

    detail = build_photo_detail_response(photo)
    assert detail.rating_summary is not None
    assert detail.rating_summary.average_rating == 3.0
    assert detail.rating_summary.ratings_count == 2


@pytest.mark.asyncio
async def test_get_async_session_yields_session():
    from app.database import get_async_session

    async for session in get_async_session():
        assert session is not None
        break
