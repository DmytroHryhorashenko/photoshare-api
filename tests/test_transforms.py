from unittest.mock import AsyncMock, patch

import pytest

from app.core.permissions import can_modify_photo
from app.models.user import User, UserRole
from app.schemas.transformed_photo import CropMode, ImageFormat, TransformRequest
from app.services.cloudinary import (
    build_transformation_options,
    build_transformation_type,
    build_transformed_url,
    validate_transformation_request,
)
from app.services.qr import _create_qr_image


def test_build_transformation_options():
    transformation = TransformRequest(
        width=800,
        height=600,
        crop=CropMode.FILL,
        angle=90,
        effect="grayscale",
        format=ImageFormat.WEBP,
    )
    options = build_transformation_options(transformation)
    assert options == {
        "width": 800,
        "height": 600,
        "crop": "fill",
        "angle": 90,
        "effect": "grayscale",
        "format": "webp",
    }


def test_build_transformation_type():
    transformation = TransformRequest(width=500, crop=CropMode.THUMB, effect="sepia")
    assert build_transformation_type(transformation) == "w500_c_thumb_e_sepia"


def test_validate_transformation_request_requires_option():
    with pytest.raises(ValueError, match="At least one transformation option"):
        validate_transformation_request(TransformRequest())


@patch("app.services.cloudinary._configure_cloudinary")
@patch("app.services.cloudinary.cloudinary.utils.cloudinary_url")
def test_build_transformed_url(mock_cloudinary_url, _mock_configure):
    mock_cloudinary_url.return_value = (
        "https://res.cloudinary.com/demo/image/upload/w_400/sample.jpg",
        {},
    )
    transformation = TransformRequest(width=400, format=ImageFormat.JPG)
    url = build_transformed_url("sample", transformation)
    assert url.endswith("sample.jpg")
    mock_cloudinary_url.assert_called_once_with(
        "sample",
        secure=True,
        width=400,
        format="jpg",
    )


def test_create_qr_image_returns_png_bytes():
    image_bytes = _create_qr_image("https://example.com/transformed.jpg")
    assert image_bytes.startswith(b"\x89PNG")


@pytest.mark.asyncio
@patch("app.services.qr.upload_image_bytes", new_callable=AsyncMock)
async def test_generate_qr_code_uploads_to_cloudinary(mock_upload):
    from app.services.qr import generate_qr_code

    mock_upload.return_value = "https://res.cloudinary.com/demo/qrcode.png"
    qr_url = await generate_qr_code("https://example.com/transformed.jpg")
    assert qr_url == "https://res.cloudinary.com/demo/qrcode.png"
    mock_upload.assert_awaited_once()
    uploaded_bytes = mock_upload.await_args.args[0]
    assert uploaded_bytes.startswith(b"\x89PNG")


def _make_user(user_id: int, role: UserRole) -> User:
    return User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
    )


def test_owner_can_transform_photo():
    owner = _make_user(1, UserRole.USER)
    assert can_modify_photo(photo_user_id=1, current_user=owner) is True


def test_admin_can_transform_photo():
    admin = _make_user(2, UserRole.ADMIN)
    assert can_modify_photo(photo_user_id=1, current_user=admin) is True


def test_non_owner_cannot_transform_photo():
    other_user = _make_user(3, UserRole.USER)
    assert can_modify_photo(photo_user_id=1, current_user=other_user) is False


@pytest.fixture
async def client(db_session):
    from httpx import ASGITransport, AsyncClient

    from app.dependencies import get_db
    from app.main import app

    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def db_session():
    from sqlalchemy import text

    from app.database import async_session_maker

    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            yield session
            await session.rollback()
    except Exception:
        pytest.skip("Database not available for integration tests")


@pytest.mark.asyncio
@patch("app.api.transforms.generate_qr_code", new_callable=AsyncMock)
@patch("app.api.transforms.build_transformed_url")
async def test_reject_non_owner_transform(
    mock_build_url,
    mock_generate_qr,
    client,
    db_session,
):
    owner_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "transform_owner",
            "email": "transform_owner@example.com",
            "password": "securepassword123",
        },
    )
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "transform_other",
            "email": "transform_other@example.com",
            "password": "securepassword123",
        },
    )
    other_token = (
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": "transform_other@example.com",
                "password": "securepassword123",
            },
        )
    ).json()["access_token"]

    from app.models.photo import Photo

    photo = Photo(
        user_id=owner_response.json()["id"],
        description="Transform test",
        image_url="https://example.com/photo.jpg",
        public_id="transform-test-photo",
    )
    db_session.add(photo)
    await db_session.flush()
    await db_session.refresh(photo)

    response = await client.post(
        f"/api/v1/photos/{photo.id}/transform",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"width": 300},
    )
    assert response.status_code == 403
    mock_build_url.assert_not_called()
    mock_generate_qr.assert_not_awaited()
