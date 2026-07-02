from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.core.permissions import can_delete_comment, can_edit_comment, can_modify_photo
from app.core.security import create_access_token, decode_access_token, hash_password
from app.models.user import User, UserRole
from app.schemas.rating import RatingCreate
from app.schemas.transformed_photo import CropMode, ImageFormat, TransformRequest
from app.services.cloudinary import (
    build_transformation_options,
    build_transformation_type,
    validate_transformation_request,
)
from app.utils.tags import normalize_tag_names, normalize_tag_name


def _user(user_id: int, role: UserRole = UserRole.USER) -> User:
    return User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
    )


def test_rating_create_rejects_values_outside_range():
    with pytest.raises(ValidationError):
        RatingCreate(value=0)
    with pytest.raises(ValidationError):
        RatingCreate(value=6)


def test_rating_create_accepts_valid_values():
    assert RatingCreate(value=1).value == 1
    assert RatingCreate(value=5).value == 5


def test_normalize_tag_name_handles_empty_after_strip():
    with pytest.raises(ValueError, match="Tag cannot be empty"):
        normalize_tag_name("   ")


def test_normalize_tag_names_rejects_duplicate_empty_entries():
    with pytest.raises(ValueError, match="Tags cannot be empty"):
        normalize_tag_names(["valid", "   "])


def test_normalize_tag_name_rejects_too_long():
    with pytest.raises(ValueError, match="Tag must be at most 100 characters"):
        normalize_tag_name("x" * 101)


def test_normalize_tag_names_rejects_too_long_tag():
    with pytest.raises(ValueError, match="Each tag must be at most 100 characters"):
        normalize_tag_names(["x" * 101])


def test_photo_create_schema_validates_tags():
    from app.schemas.photo import PhotoCreate

    with pytest.raises(ValueError, match="at most 5 tags"):
        PhotoCreate.validate_tags(["a", "b", "c", "d", "e", "f"])
    with pytest.raises(ValueError, match="Tags cannot be empty"):
        PhotoCreate.validate_tags(["valid", "  "])
    with pytest.raises(ValueError, match="at most 100 characters"):
        PhotoCreate.validate_tags(["x" * 101])
    assert PhotoCreate.validate_tags([" Nature ", "TRAVEL"]) == ["nature", "travel"]


def test_photo_update_schema_validates_tags():
    from app.schemas.photo import PhotoUpdate

    with pytest.raises(ValueError, match="at most 5 tags"):
        PhotoUpdate.validate_tags(["1", "2", "3", "4", "5", "6"])
    assert PhotoUpdate.validate_tags(None) is None


def test_transform_request_accepts_partial_options():
    request = TransformRequest(width=640, format=ImageFormat.PNG)
    validate_transformation_request(request)
    assert build_transformation_options(request) == {"width": 640, "format": "png"}
    assert build_transformation_type(request) == "w640_f_png"


def test_transform_request_crop_modes():
    request = TransformRequest(crop=CropMode.PAD, height=200)
    options = build_transformation_options(request)
    assert options["crop"] == "pad"
    assert options["height"] == 200


def test_comment_create_schema_rejects_empty_text():
    from app.schemas.comment import CommentCreate

    with pytest.raises(ValidationError):
        CommentCreate(text="   ")
    token = create_access_token(
        data={"sub": "99", "role": "user"},
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(token)


def test_hash_password_produces_bcrypt_hash():
    hashed = hash_password("another-secure-password")
    assert hashed.startswith("$2")


def test_permissions_matrix():
    owner = _user(1)
    other = _user(2)
    moderator = _user(3, UserRole.MODERATOR)
    admin = _user(4, UserRole.ADMIN)

    assert can_modify_photo(1, owner) is True
    assert can_modify_photo(1, admin) is True
    assert can_modify_photo(1, other) is False

    assert can_edit_comment(1, owner) is True
    assert can_edit_comment(1, admin) is False

    assert can_delete_comment(other) is False
    assert can_delete_comment(moderator) is True
    assert can_delete_comment(admin) is True
