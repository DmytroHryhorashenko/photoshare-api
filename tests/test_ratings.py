import pytest

from app.core.permissions import can_delete_comment
from app.models.user import User, UserRole


def _make_user(user_id: int, role: UserRole) -> User:
    return User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        password_hash="hashed",
        role=role,
        is_active=True,
    )


def test_can_delete_rating_requires_moderator_or_admin():
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


async def _create_photo(db_session, user_id: int, public_id_suffix: str) -> int:
    from app.models.photo import Photo

    photo = Photo(
        user_id=user_id,
        description="Test photo",
        image_url="https://example.com/photo.jpg",
        public_id=f"test-photo-{public_id_suffix}",
    )
    db_session.add(photo)
    await db_session.flush()
    await db_session.refresh(photo)
    return photo.id


@pytest.mark.asyncio
async def test_create_rating(client, db_session):
    owner = await _register_user(client, "rating_owner", "rating_owner@example.com")
    rater = await _register_user(client, "rating_user", "rating_user@example.com")
    rater_token = await _login(client, "rating_user@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "create-rating")

    response = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {rater_token}"},
        json={"value": 5},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["photo_id"] == photo_id
    assert data["user_id"] == rater["id"]
    assert data["value"] == 5


@pytest.mark.asyncio
async def test_reject_own_photo_rating(client, db_session):
    owner = await _register_user(client, "self_rating_owner", "self_rating_owner@example.com")
    owner_token = await _login(client, "self_rating_owner@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "self-rating")

    response = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"value": 4},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot rate your own photo"


@pytest.mark.asyncio
async def test_reject_duplicate_rating(client, db_session):
    owner = await _register_user(client, "dup_owner", "dup_owner@example.com")
    rater = await _register_user(client, "dup_rater", "dup_rater@example.com")
    rater_token = await _login(client, "dup_rater@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "dup-rating")

    first = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {rater_token}"},
        json={"value": 3},
    )
    assert first.status_code == 201

    second = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {rater_token}"},
        json={"value": 5},
    )
    assert second.status_code == 400
    assert second.json()["detail"] == "You have already rated this photo"


@pytest.mark.asyncio
async def test_calculate_average_rating(client, db_session):
    owner = await _register_user(client, "avg_owner", "avg_owner@example.com")
    rater_one = await _register_user(client, "avg_rater1", "avg_rater1@example.com")
    rater_two = await _register_user(client, "avg_rater2", "avg_rater2@example.com")
    token_one = await _login(client, "avg_rater1@example.com")
    token_two = await _login(client, "avg_rater2@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "avg-rating")

    await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {token_one}"},
        json={"value": 4},
    )
    await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {token_two}"},
        json={"value": 2},
    )

    response = await client.get(f"/api/v1/photos/{photo_id}/ratings")
    assert response.status_code == 200
    data = response.json()
    assert data["photo_id"] == photo_id
    assert data["average_rating"] == 3.0
    assert data["ratings_count"] == 2


@pytest.mark.asyncio
async def test_moderator_can_delete_rating(client, db_session):
    owner = await _register_user(client, "del_rating_owner", "del_rating_owner@example.com")
    rater = await _register_user(client, "del_rating_rater", "del_rating_rater@example.com")
    moderator = await _register_user(client, "del_rating_mod", "del_rating_mod@example.com")

    from app.repository.users import set_user_role

    await set_user_role(db_session, moderator["id"], UserRole.MODERATOR)
    await db_session.commit()

    rater_token = await _login(client, "del_rating_rater@example.com")
    moderator_token = await _login(client, "del_rating_mod@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "del-rating")

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {rater_token}"},
        json={"value": 5},
    )
    rating_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {moderator_token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Rating deleted successfully"


@pytest.mark.asyncio
async def test_reject_normal_user_delete_rating(client, db_session):
    owner = await _register_user(client, "del_user_owner", "del_user_owner@example.com")
    rater = await _register_user(client, "del_user_rater", "del_user_rater@example.com")
    other = await _register_user(client, "del_user_other", "del_user_other@example.com")
    rater_token = await _login(client, "del_user_rater@example.com")
    other_token = await _login(client, "del_user_other@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "del-user-rating")

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {rater_token}"},
        json={"value": 4},
    )
    rating_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_rate_missing_photo(client):
    await _register_user(client, "rate_missing", "rate_missing@example.com")
    token = await _login(client, "rate_missing@example.com")

    response = await client.post(
        "/api/v1/photos/99999/ratings",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 5},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rate_photo_invalid_value(client, db_session):
    owner = await _register_user(client, "invalid_owner", "invalid_owner@example.com")
    rater = await _register_user(client, "invalid_rater", "invalid_rater@example.com")
    token = await _login(client, "invalid_rater@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "invalid-value")

    response = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 6},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_ratings_missing_photo(client):
    response = await client.get("/api/v1/photos/99999/ratings")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_rating(client, db_session):
    moderator = await _register_user(client, "del_rate_mod", "del_rate_mod@example.com")
    from app.repository.users import set_user_role

    await set_user_role(db_session, moderator["id"], UserRole.MODERATOR)
    await db_session.commit()
    token = await _login(client, "del_rate_mod@example.com")

    response = await client.delete(
        "/api/v1/ratings/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_delete_rating(client, db_session):
    owner = await _register_user(client, "admin_rate_owner", "admin_rate_owner@example.com")
    rater = await _register_user(client, "admin_rate_rater", "admin_rate_rater@example.com")
    admin = await _register_user(client, "admin_rate_admin", "admin_rate_admin@example.com")
    from app.repository.users import set_user_role

    await set_user_role(db_session, admin["id"], UserRole.ADMIN)
    await db_session.commit()
    rater_token = await _login(client, "admin_rate_rater@example.com")
    admin_token = await _login(client, "admin_rate_admin@example.com")
    photo_id = await _create_photo(db_session, owner["id"], "admin-del-rating")

    create_response = await client.post(
        f"/api/v1/photos/{photo_id}/ratings",
        headers={"Authorization": f"Bearer {rater_token}"},
        json={"value": 5},
    )
    rating_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_response.status_code == 200
