"""Direct API handler tests to exercise route logic and improve coverage."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from io import BytesIO

import uuid

from starlette.datastructures import Headers

from app.api import auth as auth_api
from app.api import comments as comments_api
from app.api import photos as photos_api
from app.api import ratings as ratings_api
from app.api import search as search_api
from app.api import transforms as transforms_api
from app.api import users as users_api
from app.models.comment import Comment
from app.models.photo import Photo
from app.models.rating import Rating
from app.models.user import User, UserRole
from app.schemas.photo import PhotoUpdate
from app.schemas.auth import UserLogin, UserRegister
from app.schemas.comment import CommentCreate, CommentUpdate
from app.schemas.rating import RatingCreate
from app.schemas.transformed_photo import TransformRequest
from app.schemas.user import UserRoleUpdate, UserUpdate
from tests.helpers import create_photo_in_db, make_jpeg_bytes


async def _persist_user(db_session, role: UserRole = UserRole.USER) -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"handler{suffix}",
        email=f"handler{suffix}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_auth_register_login_handlers(db_session):
    user = await auth_api.register(
        UserRegister(
            username="handler_reg",
            email="handler_reg@example.com",
            password="securepassword123",
        ),
        db=db_session,
    )
    assert user.username == "handler_reg"

    token = await auth_api.login(
        UserLogin(email="handler_reg@example.com", password="securepassword123"),
        db=db_session,
    )
    assert token.access_token


@pytest.mark.asyncio
async def test_users_handlers(db_session):
    current = await _persist_user(db_session, UserRole.ADMIN)

    me = await users_api.get_me(current_user=current)
    assert me.id == current.id

    updated = await users_api.update_me(
        UserUpdate(username="handler_renamed"),
        db=db_session,
        current_user=current,
    )
    assert updated.username == "handler_renamed"

    profile = await users_api.get_user_profile("handler_renamed", db=db_session)
    assert profile.username == "handler_renamed"

    banned = await users_api.ban_user(current.id, db=db_session, _=current)
    assert banned.is_active is False

    unbanned = await users_api.unban_user(current.id, db=db_session, _=current)
    assert unbanned.is_active is True

    role_changed = await users_api.update_user_role(
        current.id,
        UserRoleUpdate(role=UserRole.MODERATOR),
        db=db_session,
        _=current,
    )
    assert role_changed.role == UserRole.MODERATOR


@pytest.mark.asyncio
async def test_comments_handlers(db_session):
    owner = await _persist_user(db_session)
    photo = await create_photo_in_db(db_session, owner.id, public_id="handler-photo")
    await db_session.commit()

    created = await comments_api.create_photo_comment(
        photo.id,
        CommentCreate(text="  Nice  "),
        db=db_session,
        current_user=owner,
    )
    assert created.text == "Nice"

    listed = await comments_api.list_photo_comments(photo.id, db=db_session)
    assert len(listed) == 1

    updated = await comments_api.update_photo_comment(
        created.id,
        CommentUpdate(text="Updated"),
        db=db_session,
        current_user=owner,
    )
    assert updated.text == "Updated"

    moderator = await _persist_user(db_session, UserRole.MODERATOR)
    deleted = await comments_api.delete_photo_comment(
        created.id,
        db=db_session,
        current_user=moderator,
    )
    assert deleted["message"] == "Comment deleted successfully"


@pytest.mark.asyncio
async def test_ratings_handlers(db_session):
    owner = await _persist_user(db_session)
    rater = await _persist_user(db_session)
    photo = await create_photo_in_db(db_session, owner.id, public_id="rating-handler-photo")
    await db_session.commit()

    rating = await ratings_api.rate_photo(
        photo.id,
        RatingCreate(value=5),
        db=db_session,
        current_user=rater,
    )
    assert rating.value == 5

    summary = await ratings_api.get_photo_rating_summary(photo.id, db=db_session)
    assert summary.average_rating == 5.0

    admin = await _persist_user(db_session, UserRole.ADMIN)
    deleted = await ratings_api.delete_photo_rating(
        rating.id,
        db=db_session,
        current_user=admin,
    )
    assert deleted["message"] == "Rating deleted successfully"


@pytest.mark.asyncio
@patch("app.api.photos.delete_cloudinary_photo", new_callable=AsyncMock)
@patch("app.api.photos.upload_photo", new_callable=AsyncMock)
async def test_photos_handlers(mock_upload, mock_delete, db_session):
    mock_upload.return_value = {
        "image_url": "https://cdn.example.com/handler.jpg",
        "public_id": "handler-upload",
    }
    owner = await _persist_user(db_session)
    await db_session.commit()

    upload = UploadFile(
        filename="photo.jpg",
        file=BytesIO(make_jpeg_bytes()),
        headers=Headers({"content-type": "image/jpeg"}),
    )
    created = await photos_api.upload_user_photo(
        file=upload,
        description="Handler photo",
        tags=["nature", "sky"],
        db=db_session,
        current_user=owner,
    )
    assert len(created.tags) == 2

    detail = await photos_api.get_photo(created.id, db=db_session)
    assert detail.id == created.id

    updated = await photos_api.update_user_photo(
        created.id,
        PhotoUpdate(description="Updated handler photo"),
        db=db_session,
        current_user=owner,
    )
    assert updated.description == "Updated handler photo"

    deleted = await photos_api.delete_user_photo(
        created.id,
        db=db_session,
        current_user=owner,
    )
    assert deleted["message"] == "Photo deleted successfully"
    mock_delete.assert_awaited()


@pytest.mark.asyncio
@patch("app.api.transforms.generate_qr_code", new_callable=AsyncMock)
@patch("app.api.transforms.build_transformed_url")
async def test_transforms_handlers(mock_build_url, mock_generate_qr, db_session):
    mock_build_url.return_value = "https://cdn.example.com/transformed.jpg"
    mock_generate_qr.return_value = "https://cdn.example.com/qr.png"

    owner = await _persist_user(db_session)
    photo = await create_photo_in_db(db_session, owner.id, public_id="transform-handler")
    await db_session.commit()

    transformed = await transforms_api.create_photo_transformation(
        photo.id,
        TransformRequest(width=300),
        db=db_session,
        current_user=owner,
    )
    assert transformed.transformed_url.endswith("transformed.jpg")

    transforms = await transforms_api.list_photo_transformations(photo.id, db=db_session)
    assert len(transforms) == 1

    fetched = await transforms_api.get_transformation(transforms[0].id, db=db_session)
    assert fetched.id == transforms[0].id


@pytest.mark.asyncio
async def test_search_handler(db_session):
    owner = await _persist_user(db_session)
    photo = await create_photo_in_db(
        db_session,
        owner.id,
        public_id="search-handler",
        description="mountain view",
    )
    await db_session.commit()

    results = await search_api.search_photos(
        keyword="mountain",
        tag=None,
        min_rating=None,
        sort_by="date",
        order="desc",
        user_id=None,
        db=db_session,
        current_user=None,
    )
    assert len(results) == 1


@pytest.mark.asyncio
async def test_get_current_user_and_optional_user(db_session):
    from app.dependencies import get_current_user, get_optional_current_user
    from app.core.security import create_access_token
    from datetime import timedelta

    user = await _persist_user(db_session)
    await db_session.commit()

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=5),
    )
    resolved = await get_current_user(token=token, db=db_session)
    assert resolved.id == user.id

    optional = await get_optional_current_user(token=token, db=db_session)
    assert optional is not None
    assert optional.id == user.id

    assert await get_optional_current_user(token=None, db=db_session) is None


@pytest.mark.asyncio
async def test_api_handler_forbidden_and_validation_paths(db_session):
    owner = await _persist_user(db_session)
    other = await _persist_user(db_session)
    photo = await create_photo_in_db(db_session, owner.id, public_id="forbidden-handler")
    await db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await photos_api.update_user_photo(
            photo.id,
            PhotoUpdate(description="Nope"),
            db=db_session,
            current_user=other,
        )
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException) as exc:
        await ratings_api.rate_photo(
            photo.id,
            RatingCreate(value=4),
            db=db_session,
            current_user=owner,
        )
    assert exc.value.status_code == 400

    rater = await _persist_user(db_session)
    first = await ratings_api.rate_photo(
        photo.id,
        RatingCreate(value=3),
        db=db_session,
        current_user=rater,
    )
    assert first.id is not None

    with pytest.raises(HTTPException) as exc:
        await ratings_api.rate_photo(
            photo.id,
            RatingCreate(value=5),
            db=db_session,
            current_user=rater,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_api_handler_not_found_paths(db_session):
    owner = await _persist_user(db_session)
    moderator = await _persist_user(db_session, UserRole.MODERATOR)
    await db_session.flush()

    with pytest.raises(HTTPException) as exc:
        await comments_api.create_photo_comment(
            99999,
            CommentCreate(text="missing"),
            db=db_session,
            current_user=owner,
        )
    assert exc.value.status_code == 404

    with pytest.raises(HTTPException) as exc:
        await ratings_api.rate_photo(
            99999,
            RatingCreate(value=5),
            db=db_session,
            current_user=owner,
        )
    assert exc.value.status_code == 404

    with pytest.raises(HTTPException) as exc:
        await photos_api.get_photo(99999, db=db_session)
    assert exc.value.status_code == 404
