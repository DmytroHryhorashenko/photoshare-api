"""Unit and integration tests for service layer."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile

from app.schemas.auth import UserRegister
from app.schemas.transformed_photo import ImageFormat, TransformRequest
from app.services import auth as auth_service
from app.services import cloudinary as cloudinary_service
from app.services import qr as qr_service


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(db_session):
    await auth_service.register_user(
        db_session,
        UserRegister(
            username="auth_pw",
            email="auth_pw@example.com",
            password="securepassword123",
        ),
    )
    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate_user(
            db_session,
            "auth_pw@example.com",
            "wrong-password",
        )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticate_user_inactive(db_session):
    user = await auth_service.register_user(
        db_session,
        UserRegister(
            username="inactive_svc",
            email="inactive_svc@example.com",
            password="securepassword123",
        ),
    )
    from app.repository.users import set_user_active_status

    await set_user_active_status(db_session, user.id, False)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate_user(
            db_session,
            "inactive_svc@example.com",
            "securepassword123",
        )
    assert exc.value.status_code == 401
    assert exc.value.detail == "Inactive user account"


@pytest.mark.asyncio
async def test_register_user_duplicate_username(db_session):
    await auth_service.register_user(
        db_session,
        UserRegister(
            username="dup_user",
            email="first@example.com",
            password="securepassword123",
        ),
    )
    with pytest.raises(HTTPException) as exc:
        await auth_service.register_user(
            db_session,
            UserRegister(
                username="dup_user",
                email="second@example.com",
                password="securepassword123",
            ),
        )
    assert exc.value.status_code == 400
    assert exc.value.detail == "Username already taken"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(db_session):
    await auth_service.register_user(
        db_session,
        UserRegister(
            username="dup_email_a",
            email="dup_email@example.com",
            password="securepassword123",
        ),
    )
    with pytest.raises(HTTPException) as exc:
        await auth_service.register_user(
            db_session,
            UserRegister(
                username="dup_email_b",
                email="dup_email@example.com",
                password="securepassword123",
            ),
        )
    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already registered"


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session):
    await auth_service.register_user(
        db_session,
        UserRegister(
            username="auth_ok",
            email="auth_ok@example.com",
            password="securepassword123",
        ),
    )
    user = await auth_service.authenticate_user(
        db_session,
        "auth_ok@example.com",
        "securepassword123",
    )
    assert user.email == "auth_ok@example.com"


@pytest.mark.asyncio
async def test_logout_user_blacklists_token(db_session):
    user_data = UserRegister(
        username="logout_user",
        email="logout@example.com",
        password="securepassword123",
    )
    user = await auth_service.register_user(db_session, user_data)
    assert user.id is not None

    token = "test-token-value"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    await auth_service.logout_user(db_session, token, expires_at)
    assert await auth_service.is_token_blacklisted(db_session, token) is True


@pytest.mark.asyncio
async def test_logout_user_idempotent_for_blacklisted_token(db_session):
    token = "already-blacklisted"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    await auth_service.blacklist_token(db_session, token, expires_at)
    await db_session.commit()

    await auth_service.logout_user(db_session, token, expires_at)
    assert await auth_service.is_token_blacklisted(db_session, token) is True


@patch("app.services.cloudinary.settings")
def test_configure_cloudinary_missing_credentials(mock_settings):
    mock_settings.cloudinary_name = ""
    mock_settings.cloudinary_api_key = ""
    mock_settings.cloudinary_api_secret = ""
    with pytest.raises(HTTPException) as exc:
        cloudinary_service._configure_cloudinary()
    assert exc.value.status_code == 500
    assert "Cloudinary is not configured" in exc.value.detail


def test_build_transformation_options_skips_auto_format():
    request = TransformRequest(width=100, format=ImageFormat.AUTO)
    options = cloudinary_service.build_transformation_options(request)
    assert options == {"width": 100}
    assert "format" not in options


def test_build_transformation_type_all_fields():
    request = TransformRequest(
        width=100,
        height=200,
        crop="fill",
        angle=45,
        effect="sepia",
        format=ImageFormat.WEBP,
    )
    result = cloudinary_service.build_transformation_type(request)
    assert "w100" in result
    assert "h200" in result
    assert "c_fill" in result


@patch("app.services.cloudinary._configure_cloudinary")
@patch("app.services.cloudinary.cloudinary.utils.cloudinary_url")
def test_build_transformed_url(mock_url, _mock_configure):
    mock_url.return_value = ("https://cdn.example.com/img.jpg", {})
    url = cloudinary_service.build_transformed_url(
        "sample",
        TransformRequest(width=300),
    )
    assert url == "https://cdn.example.com/img.jpg"


@pytest.mark.asyncio
@patch("app.services.cloudinary._configure_cloudinary")
async def test_upload_photo_rejects_empty_file(_mock_configure):
    upload = UploadFile(filename="empty.jpg", file=BytesIO(b""))
    with pytest.raises(HTTPException) as exc:
        await cloudinary_service.upload_photo(upload)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Uploaded file is empty"


@pytest.mark.asyncio
@patch("app.services.cloudinary.asyncio.to_thread", new_callable=AsyncMock)
@patch("app.services.cloudinary._configure_cloudinary")
async def test_upload_photo_cloudinary_failure(_mock_configure, mock_to_thread):
    mock_to_thread.side_effect = RuntimeError("network error")
    upload = UploadFile(filename="photo.jpg", file=BytesIO(b"image-bytes"))
    with pytest.raises(HTTPException) as exc:
        await cloudinary_service.upload_photo(upload)
    assert exc.value.status_code == 500
    assert "Failed to upload image" in exc.value.detail


@pytest.mark.asyncio
@patch("app.services.cloudinary.asyncio.to_thread", new_callable=AsyncMock)
@patch("app.services.cloudinary._configure_cloudinary")
async def test_upload_photo_success(_mock_configure, mock_to_thread):
    mock_to_thread.return_value = {
        "secure_url": "https://cdn.example.com/photo.jpg",
        "public_id": "photoshare/photo123",
    }
    upload = UploadFile(filename="photo.jpg", file=BytesIO(b"image-bytes"))
    result = await cloudinary_service.upload_photo(upload)
    assert result["image_url"] == "https://cdn.example.com/photo.jpg"
    assert result["public_id"] == "photoshare/photo123"


@pytest.mark.asyncio
@patch("app.services.cloudinary.asyncio.to_thread", new_callable=AsyncMock)
@patch("app.services.cloudinary._configure_cloudinary")
async def test_upload_image_bytes_success(_mock_configure, mock_to_thread):
    mock_to_thread.return_value = {"secure_url": "https://cdn.example.com/qr.png"}
    url = await cloudinary_service.upload_image_bytes(
        b"\x89PNG",
        folder="photoshare/qrcodes",
        public_id_prefix="qr_test",
    )
    assert url == "https://cdn.example.com/qr.png"


@pytest.mark.asyncio
@patch("app.services.cloudinary.asyncio.to_thread", new_callable=AsyncMock)
@patch("app.services.cloudinary._configure_cloudinary")
async def test_upload_image_bytes_failure(_mock_configure, mock_to_thread):
    mock_to_thread.side_effect = RuntimeError("upload failed")
    with pytest.raises(HTTPException) as exc:
        await cloudinary_service.upload_image_bytes(
            b"bytes",
            folder="f",
            public_id_prefix="p",
        )
    assert exc.value.status_code == 500


@pytest.mark.asyncio
@patch("app.services.cloudinary.asyncio.to_thread", new_callable=AsyncMock)
@patch("app.services.cloudinary._configure_cloudinary")
async def test_delete_photo_cloudinary_failure(_mock_configure, mock_to_thread):
    mock_to_thread.side_effect = RuntimeError("delete failed")
    with pytest.raises(HTTPException) as exc:
        await cloudinary_service.delete_photo("public-id")
    assert exc.value.status_code == 500


@pytest.mark.asyncio
@patch("app.services.cloudinary.asyncio.to_thread", new_callable=AsyncMock)
@patch("app.services.cloudinary._configure_cloudinary")
async def test_delete_photo_success(_mock_configure, mock_to_thread):
    mock_to_thread.return_value = {"result": "ok"}
    await cloudinary_service.delete_photo("public-id")
    mock_to_thread.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.qr.upload_image_bytes", new_callable=AsyncMock)
async def test_generate_qr_code_success(mock_upload):
    mock_upload.return_value = "https://cdn.example.com/qr.png"
    url = await qr_service.generate_qr_code("https://example.com/photo")
    assert url == "https://cdn.example.com/qr.png"


@pytest.mark.asyncio
@patch("app.services.qr.upload_image_bytes", new_callable=AsyncMock)
async def test_generate_qr_code_propagates_http_exception(mock_upload):
    mock_upload.side_effect = HTTPException(status_code=500, detail="upload failed")
    with pytest.raises(HTTPException):
        await qr_service.generate_qr_code("https://example.com/photo")


@pytest.mark.asyncio
@patch("app.services.qr._create_qr_image", side_effect=RuntimeError("qr fail"))
async def test_generate_qr_code_wraps_unexpected_error(_mock_create):
    with pytest.raises(HTTPException) as exc:
        await qr_service.generate_qr_code("https://example.com/photo")
    assert exc.value.status_code == 500
    assert exc.value.detail == "Failed to generate QR code"
