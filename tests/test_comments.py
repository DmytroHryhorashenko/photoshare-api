import pytest

from app.core.permissions import can_delete_comment, can_edit_comment
from app.models.user import User, UserRole
from app.utils.comments import normalize_comment_text


def test_normalize_comment_text_strips_whitespace():
    assert normalize_comment_text("  hello world  ") == "hello world"


def test_normalize_comment_text_rejects_empty():
    with pytest.raises(ValueError, match="Comment text cannot be empty"):
        normalize_comment_text("   ")


def _make_user(user_id: int, role: UserRole) -> User:
    return User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
    )


def test_can_edit_comment_owner_only():
    owner = _make_user(1, UserRole.USER)
    admin = _make_user(2, UserRole.ADMIN)
    moderator = _make_user(3, UserRole.MODERATOR)
    other_user = _make_user(4, UserRole.USER)

    assert can_edit_comment(comment_user_id=1, current_user=owner) is True
    assert can_edit_comment(comment_user_id=1, current_user=admin) is False
    assert can_edit_comment(comment_user_id=1, current_user=moderator) is False
    assert can_edit_comment(comment_user_id=1, current_user=other_user) is False


def test_can_delete_comment_moderator_or_admin_only():
    user = _make_user(1, UserRole.USER)
    moderator = _make_user(2, UserRole.MODERATOR)
    admin = _make_user(3, UserRole.ADMIN)

    assert can_delete_comment(user) is False
    assert can_delete_comment(moderator) is True
    assert can_delete_comment(admin) is True


async def _register_user(client, username: str, email: str) -> dict:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    return response.json()


async def _login(client, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "securepassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


async def _create_photo(db_session, user_id: int) -> int:
    from app.models.photo import Photo

    photo = Photo(
        user_id=user_id,
        description="Test photo",
        image_url="https://example.com/photo.jpg",
        public_id=f"test-photo-{user_id}",
    )
    db_session.add(photo)
    await db_session.flush()
    await db_session.refresh(photo)
    return photo.id


@pytest.mark.asyncio
async def test_create_comment(client, db_session):
    user = await _register_user(client, "commenter", "commenter@example.com")
    token = await _login(client, "commenter@example.com")
    photo_id = await _create_photo(db_session, user["id"])

    response = await client.post(
        f"/api/v1/photos/{photo_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "  Great shot!  "},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Great shot!"
    assert data["photo_id"] == photo_id
    assert data["user_id"] == user["id"]


@pytest.mark.asyncio
async def test_edit_own_comment(client, db_session):
    user = await _register_user(client, "comment_editor", "comment_editor@example.com")
    token = await _login(client, "comment_editor@example.com")
    photo_id = await _create_photo(db_session, user["id"])

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Original comment"},
    )
    comment_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Updated comment"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["text"] == "Updated comment"


@pytest.mark.asyncio
async def test_reject_edit_other_user_comment(client, db_session):
    owner = await _register_user(client, "comment_owner", "comment_owner@example.com")
    other = await _register_user(client, "comment_other", "comment_other@example.com")
    owner_token = await _login(client, "comment_owner@example.com")
    other_token = await _login(client, "comment_other@example.com")
    photo_id = await _create_photo(db_session, owner["id"])

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/comments",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"text": "Owner comment"},
    )
    comment_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"text": "Hijacked comment"},
    )
    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_moderator_can_delete_comment(client, db_session):
    owner = await _register_user(client, "delete_owner", "delete_owner@example.com")
    moderator = await _register_user(client, "delete_mod", "delete_mod@example.com")

    from app.models.user import UserRole
    from app.repository.users import set_user_role

    await set_user_role(db_session, moderator["id"], UserRole.MODERATOR)
    await db_session.commit()

    owner_token = await _login(client, "delete_owner@example.com")
    moderator_token = await _login(client, "delete_mod@example.com")
    photo_id = await _create_photo(db_session, owner["id"])

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/comments",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"text": "Delete me"},
    )
    comment_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Comment deleted successfully"


@pytest.mark.asyncio
async def test_reject_normal_user_delete_comment(client, db_session):
    owner = await _register_user(client, "delete_user_owner", "delete_user_owner@example.com")
    other = await _register_user(client, "delete_user_other", "delete_user_other@example.com")
    owner_token = await _login(client, "delete_user_owner@example.com")
    other_token = await _login(client, "delete_user_other@example.com")
    photo_id = await _create_photo(db_session, owner["id"])

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/comments",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"text": "Protected comment"},
    )
    comment_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_list_photo_comments(client, db_session):
    user = await _register_user(client, "list_comments", "list_comments@example.com")
    token = await _login(client, "list_comments@example.com")
    photo_id = await _create_photo(db_session, user["id"])

    await client.post(
        f"/api/v1/photos/{photo_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "First"},
    )
    response = await client.get(f"/api/v1/photos/{photo_id}/comments")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_create_comment_missing_photo(client):
    await _register_user(client, "comment_missing", "comment_missing@example.com")
    token = await _login(client, "comment_missing@example.com")

    response = await client.post(
        "/api/v1/photos/99999/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Hello"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_comments_missing_photo(client):
    response = await client.get("/api/v1/photos/99999/comments")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_edit_missing_comment(client):
    await _register_user(client, "edit_missing", "edit_missing@example.com")
    token = await _login(client, "edit_missing@example.com")

    response = await client.put(
        "/api/v1/comments/99999",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Updated"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_comment(client, db_session):
    await _register_user(client, "del_missing_mod", "del_missing_mod@example.com")
    from app.repository.users import set_user_role

    mod = await _register_user(client, "del_missing_mod2", "del_missing_mod2@example.com")
    await set_user_role(db_session, mod["id"], UserRole.MODERATOR)
    await db_session.commit()
    token = await _login(client, "del_missing_mod2@example.com")

    response = await client.delete(
        "/api/v1/comments/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
