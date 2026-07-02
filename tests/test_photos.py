import pytest

from app.core.permissions import can_modify_photo
from app.models.user import User, UserRole
from app.utils.tags import normalize_tag_names


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


def _make_user(user_id: int, role: UserRole) -> User:
    user = User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
    )
    return user


def test_can_modify_photo_owner():
    owner = _make_user(1, UserRole.USER)
    assert can_modify_photo(photo_user_id=1, current_user=owner) is True


def test_can_modify_photo_admin():
    admin = _make_user(2, UserRole.ADMIN)
    assert can_modify_photo(photo_user_id=1, current_user=admin) is True


def test_can_modify_photo_denied_for_other_user():
    other_user = _make_user(3, UserRole.USER)
    assert can_modify_photo(photo_user_id=1, current_user=other_user) is False
