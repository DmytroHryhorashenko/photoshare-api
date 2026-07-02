import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock, patch

from app.api.photos import build_photo_detail_response, validate_image_file
from app.core.permissions import can_modify_photo, require_owner_or_admin
from app.models.photo import Photo
from app.models.rating import Rating
from app.models.user import User, UserRole
from app.schemas.photo import PhotoCreate, PhotoUpdate
from app.utils.tags import normalize_tag_names
from fastapi import HTTPException, UploadFile
from io import BytesIO
from starlette.datastructures import Headers

from tests.helpers import (
    auth_header,
    create_photo_in_db,
    login_user,
    make_jpeg_bytes,
    promote_to_admin,
    register_user,
)


def test_normalize_tag_names_strips_and_lowercases():
    assert normalize_tag_names(["  Nature ", "TRAVEL"]) == ["nature", "travel"]


def test_normalize_tag_names_rejects_empty():
    with pytest.raises(ValueError, match="Tags cannot be empty"):
        normalize_tag_names(["valid", "   "])


def test_normalize_tag_names_rejects_more_than_five():
    with pytest.raises(ValueError, match="at most 5 tags"):
        normalize_tag_names(["a", "b", "c", "d", "e", "f"])


def test_normalize_tag_names_empty_input():
    assert normalize_tag_names(None) == []
    assert normalize_tag_names([]) == []


def test_photo_create_schema_none_tags():
    assert PhotoCreate(tags=None).tags is None


def test_photo_create_schema_rejects_long_tag():
    with pytest.raises(ValidationError):
        PhotoCreate(tags=["x" * 101])


def test_photo_update_schema_none_tags():
    assert PhotoUpdate(tags=None).tags is None


def test_photo_create_schema_validates_too_many_tags():
    with pytest.raises(ValidationError):
        PhotoCreate(tags=["a", "b", "c", "d", "e", "f"])


def test_photo_update_schema_validates_empty_tag():
    with pytest.raises(ValidationError):
        PhotoUpdate(tags=["valid", "  "])


def test_photo_update_schema_normalizes_tags():
    updated = PhotoUpdate(tags=[" Nature ", "CITY"])
    assert updated.tags == ["nature", "city"]


def _make_user(user_id: int, role: UserRole) -> User:
    return User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
    )


def test_can_modify_photo_owner():
    owner = _make_user(1, UserRole.USER)
    assert can_modify_photo(photo_user_id=1, current_user=owner) is True


def test_can_modify_photo_admin():
    admin = _make_user(2, UserRole.ADMIN)
    assert can_modify_photo(photo_user_id=1, current_user=admin) is True


def test_can_modify_photo_denied_for_other_user():
    other_user = _make_user(3, UserRole.USER)
    assert can_modify_photo(photo_user_id=1, current_user=other_user) is False


def test_validate_image_file_rejects_non_image():
    upload = UploadFile(
        filename="doc.pdf",
        file=BytesIO(b"data"),
        headers=Headers({"content-type": "application/pdf"}),
    )
    with pytest.raises(HTTPException) as exc:
        validate_image_file(upload)
    assert exc.value.status_code == 400


def test_build_photo_detail_response_includes_rating_summary():
    from datetime import datetime, timezone

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
    photo.tags = []
    photo.comments = []
    photo.transformed_photos = []
    photo.ratings = [
        Rating(
            id=1,
            photo_id=1,
            user_id=2,
            value=4,
            created_at=now,
        ),
        Rating(
            id=2,
            photo_id=1,
            user_id=3,
            value=2,
            created_at=now,
        ),
    ]
    detail = build_photo_detail_response(photo)
    assert detail.rating_summary is not None
    assert detail.rating_summary.average_rating == 3.0
    assert detail.rating_summary.ratings_count == 2


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
@patch("app.api.photos.upload_photo", new_callable=AsyncMock)
async def test_upload_photo_success(mock_upload, mock_delete, client):
    mock_upload.return_value = {
        "image_url": "https://cdn.example.com/photo.jpg",
        "public_id": "cloud-photo-1",
    }
    user = await register_user(client, "upload_user", "upload@example.com")
    token = await login_user(client, "upload@example.com")

    response = await client.post(
        "/api/v1/photos",
        headers=auth_header(token),
        files=[
            ("file", ("photo.jpg", make_jpeg_bytes(), "image/jpeg")),
            ("description", (None, "My photo")),
        ],
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user["id"]
    assert data["description"] == "My photo"
    assert data["tags"] == []
    mock_delete.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
@patch("app.api.photos.upload_photo", new_callable=AsyncMock)
async def test_upload_photo_with_tags(mock_upload, mock_delete, client):
    mock_upload.return_value = {
        "image_url": "https://cdn.example.com/photo.jpg",
        "public_id": "cloud-photo-tags",
    }
    user = await register_user(client, "upload_tags", "upload_tags@example.com")
    token = await login_user(client, "upload_tags@example.com")

    response = await client.post(
        "/api/v1/photos",
        headers=auth_header(token),
        files=[
            ("file", ("photo.jpg", make_jpeg_bytes(), "image/jpeg")),
            ("tags", (None, "nature")),
            ("tags", (None, "travel")),
        ],
    )
    assert response.status_code == 201
    assert len(response.json()["tags"]) == 2


@pytest.mark.asyncio
async def test_upload_photo_rejects_non_image(client):
    await register_user(client, "bad_upload", "bad_upload@example.com")
    token = await login_user(client, "bad_upload@example.com")

    response = await client.post(
        "/api/v1/photos",
        headers=auth_header(token),
        files={"file": ("file.txt", b"not-an-image", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only image files" in response.json()["detail"]


@pytest.mark.asyncio
@patch("app.api.photos.upload_photo", new_callable=AsyncMock)
async def test_upload_photo_rejects_too_many_tags(mock_upload, client):
    await register_user(client, "tag_upload", "tag_upload@example.com")
    token = await login_user(client, "tag_upload@example.com")

    response = await client.post(
        "/api/v1/photos",
        headers=auth_header(token),
        files=[
            ("file", ("photo.jpg", make_jpeg_bytes(), "image/jpeg")),
            ("tags", (None, "a")),
            ("tags", (None, "b")),
            ("tags", (None, "c")),
            ("tags", (None, "d")),
            ("tags", (None, "e")),
            ("tags", (None, "f")),
        ],
    )
    assert response.status_code == 400
    mock_upload.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
@patch("app.api.photos.create_photo", new_callable=AsyncMock)
@patch("app.api.photos.upload_photo", new_callable=AsyncMock)
async def test_upload_photo_rolls_back_cloudinary_on_db_error(
    mock_upload,
    mock_create,
    mock_delete,
    client,
):
    mock_upload.return_value = {
        "image_url": "https://cdn.example.com/photo.jpg",
        "public_id": "cloud-photo-rollback",
    }
    mock_create.side_effect = RuntimeError("db failure")
    await register_user(client, "rollback_user", "rollback@example.com")
    token = await login_user(client, "rollback@example.com")

    response = await client.post(
        "/api/v1/photos",
        headers=auth_header(token),
        files={"file": ("photo.jpg", make_jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 500
    mock_delete.assert_awaited_once_with("cloud-photo-rollback")


@pytest.mark.asyncio
async def test_get_photo_detail(client, db_session):
    user = await register_user(client, "detail_user", "detail@example.com")
    photo = await create_photo_in_db(db_session, user["id"], public_id="detail-photo")
    await db_session.commit()

    response = await client.get(f"/api/v1/photos/{photo.id}")
    assert response.status_code == 200
    assert response.json()["public_id"] == "detail-photo"


@pytest.mark.asyncio
async def test_get_missing_photo_returns_404(client):
    response = await client.get("/api/v1/photos/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
async def test_update_photo_by_owner(mock_delete, client, db_session):
    user = await register_user(client, "update_owner", "update_owner@example.com")
    token = await login_user(client, "update_owner@example.com")
    photo = await create_photo_in_db(db_session, user["id"], public_id="update-photo")
    await db_session.commit()

    response = await client.put(
        f"/api/v1/photos/{photo.id}",
        headers=auth_header(token),
        json={"description": "Updated description", "tags": ["sunset"]},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"
    mock_delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_missing_photo_returns_404(client):
    await register_user(client, "update_missing", "update_missing@example.com")
    token = await login_user(client, "update_missing@example.com")

    response = await client.put(
        "/api/v1/photos/99999",
        headers=auth_header(token),
        json={"description": "Nope"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_photo_forbidden_for_other_user(client, db_session):
    owner = await register_user(client, "owner_update", "owner_update@example.com")
    other = await register_user(client, "other_update", "other_update@example.com")
    other_token = await login_user(client, "other_update@example.com")
    photo = await create_photo_in_db(db_session, owner["id"], public_id="forbidden-update")
    await db_session.commit()

    response = await client.put(
        f"/api/v1/photos/{photo.id}",
        headers=auth_header(other_token),
        json={"description": "Hack"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_update_another_users_photo(client, db_session):
    owner = await register_user(client, "photo_owner_admin", "photo_owner_admin@example.com")
    admin = await register_user(client, "photo_admin", "photo_admin@example.com")
    await promote_to_admin(db_session, admin["id"])
    admin_token = await login_user(client, "photo_admin@example.com")
    photo = await create_photo_in_db(db_session, owner["id"], public_id="admin-update")
    await db_session.commit()

    response = await client.put(
        f"/api/v1/photos/{photo.id}",
        headers=auth_header(admin_token),
        json={"description": "Admin edit"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Admin edit"


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
async def test_delete_photo_by_owner(mock_delete, client, db_session):
    user = await register_user(client, "delete_owner", "delete_owner@example.com")
    token = await login_user(client, "delete_owner@example.com")
    photo = await create_photo_in_db(db_session, user["id"], public_id="delete-photo")
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/photos/{photo.id}",
        headers=auth_header(token),
    )
    assert response.status_code == 200
    mock_delete.assert_awaited_once_with("delete-photo")


@pytest.mark.asyncio
async def test_delete_missing_photo_returns_404(client):
    await register_user(client, "delete_missing", "delete_missing@example.com")
    token = await login_user(client, "delete_missing@example.com")

    response = await client.delete(
        "/api/v1/photos/99999",
        headers=auth_header(token),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_photo_forbidden_for_other_user(client, db_session):
    owner = await register_user(client, "owner_delete", "owner_delete@example.com")
    other = await register_user(client, "other_delete", "other_delete@example.com")
    other_token = await login_user(client, "other_delete@example.com")
    photo = await create_photo_in_db(db_session, owner["id"], public_id="forbidden-delete")
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/photos/{photo.id}",
        headers=auth_header(other_token),
    )
    assert response.status_code == 403
