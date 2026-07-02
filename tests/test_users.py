import pytest

from app.models.photo import Photo
from app.models.user import UserRole
from tests.helpers import auth_header, login_user, register_user


async def _register(client, username: str, email: str) -> dict:
    return await register_user(client, username, email)


async def _login(client, email: str) -> str:
    return await login_user(client, email)


@pytest.mark.asyncio
async def test_get_current_user(client):
    user = await _register(client, "profile_me", "profile_me@example.com")
    token = await _login(client, "profile_me@example.com")

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["username"] == "profile_me"
    assert data["email"] == "profile_me@example.com"
    assert data["role"] == UserRole.ADMIN.value
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_update_own_profile(client):
    await _register(client, "profile_update", "profile_update@example.com")
    token = await _login(client, "profile_update@example.com")

    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "profile_updated",
            "email": "profile_updated@example.com",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "profile_updated"
    assert data["email"] == "profile_updated@example.com"


@pytest.mark.asyncio
async def test_reject_duplicate_email_on_profile_update(client):
    await _register(client, "profile_email_a", "profile_email_a@example.com")
    await _register(client, "profile_email_b", "profile_email_b@example.com")
    token = await _login(client, "profile_email_b@example.com")

    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "profile_email_a@example.com"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_reject_duplicate_username_on_profile_update(client):
    await _register(client, "profile_user_a", "profile_user_a@example.com")
    await _register(client, "profile_user_b", "profile_user_b@example.com")
    token = await _login(client, "profile_user_b@example.com")

    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "profile_user_a"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


@pytest.mark.asyncio
async def test_get_public_profile_by_username(client, db_session):
    user = await _register(client, "public_profile", "public_profile@example.com")

    db_session.add(
        Photo(
            user_id=user["id"],
            description="Photo one",
            image_url="https://example.com/1.jpg",
            public_id="profile-photo-1",
        )
    )
    db_session.add(
        Photo(
            user_id=user["id"],
            description="Photo two",
            image_url="https://example.com/2.jpg",
            public_id="profile-photo-2",
        )
    )
    await db_session.flush()

    response = await client.get("/api/v1/users/public_profile")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["username"] == "public_profile"
    assert data["email"] == "public_profile@example.com"
    assert data["role"] == UserRole.ADMIN.value
    assert data["is_active"] is True
    assert "created_at" in data
    assert data["uploaded_photos_count"] == 2


@pytest.mark.asyncio
async def test_admin_can_ban_user(client):
    admin = await _register(client, "ban_admin", "ban_admin@example.com")
    victim = await _register(client, "ban_victim", "ban_victim@example.com")
    admin_token = await _login(client, "ban_admin@example.com")

    response = await client.patch(
        f"/api/v1/users/{victim['id']}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == victim["id"]
    assert data["username"] == "ban_victim"
    assert data["is_active"] is False
    assert data["message"] == "User has been banned"


@pytest.mark.asyncio
async def test_admin_can_unban_user(client):
    admin = await _register(client, "unban_admin", "unban_admin@example.com")
    victim = await _register(client, "unban_victim", "unban_victim@example.com")
    admin_token = await _login(client, "unban_admin@example.com")

    await client.patch(
        f"/api/v1/users/{victim['id']}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    response = await client.patch(
        f"/api/v1/users/{victim['id']}/unban",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    assert data["message"] == "User has been unbanned"


@pytest.mark.asyncio
async def test_admin_can_change_role(client):
    admin = await _register(client, "role_admin", "role_admin@example.com")
    target = await _register(client, "role_target", "role_target@example.com")
    admin_token = await _login(client, "role_admin@example.com")

    response = await client.patch(
        f"/api/v1/users/{target['id']}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": UserRole.MODERATOR.value},
    )
    assert response.status_code == 200
    assert response.json()["role"] == UserRole.MODERATOR.value


@pytest.mark.asyncio
async def test_normal_user_cannot_ban_or_change_role(client):
    await _register(client, "perm_admin", "perm_admin@example.com")
    normal = await _register(client, "perm_normal", "perm_normal@example.com")
    normal_token = await _login(client, "perm_normal@example.com")

    ban_response = await client.patch(
        f"/api/v1/users/{normal['id']}/ban",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert ban_response.status_code == 403

    role_response = await client.patch(
        f"/api/v1/users/{normal['id']}/role",
        headers={"Authorization": f"Bearer {normal_token}"},
        json={"role": UserRole.ADMIN.value},
    )
    assert role_response.status_code == 403


@pytest.mark.asyncio
async def test_inactive_user_cannot_login(client):
    await _register(client, "inactive_admin", "inactive_admin@example.com")
    victim = await _register(client, "inactive_victim", "inactive_victim@example.com")
    admin_token = await _login(client, "inactive_admin@example.com")

    await client.patch(
        f"/api/v1/users/{victim['id']}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "inactive_victim@example.com", "password": "securepassword123"},
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Inactive user account"


@pytest.mark.asyncio
async def test_inactive_user_cannot_access_protected_route(client):
    await _register(client, "protected_admin", "protected_admin@example.com")
    victim = await _register(client, "protected_victim", "protected_victim@example.com")
    admin_token = await _login(client, "protected_admin@example.com")
    victim_token = await _login(client, "protected_victim@example.com")

    await client.patch(
        f"/api/v1/users/{victim['id']}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {victim_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user account"


@pytest.mark.asyncio
async def test_update_profile_password(client):
    await _register(client, "pwd_update", "pwd_update@example.com")
    token = await _login(client, "pwd_update@example.com")

    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "newsecurepassword99"},
    )
    assert response.status_code == 200

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "pwd_update@example.com", "password": "newsecurepassword99"},
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_get_missing_username_returns_404(client):
    response = await client.get("/api/v1/users/no_such_user")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_me_requires_fields(client):
    await _register(client, "empty_update", "empty_update@example.com")
    token = await _login(client, "empty_update@example.com")

    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


@pytest.mark.asyncio
async def test_ban_missing_user_returns_404(client):
    await _register(client, "ban_missing_admin", "ban_missing_admin@example.com")
    token = await _login(client, "ban_missing_admin@example.com")

    response = await client.patch(
        "/api/v1/users/99999/ban",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unban_missing_user_returns_404(client):
    await _register(client, "unban_missing_admin", "unban_missing_admin@example.com")
    token = await _login(client, "unban_missing_admin@example.com")

    response = await client.patch(
        "/api/v1/users/99999/unban",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_change_role_missing_user_returns_404(client):
    await _register(client, "role_missing_admin", "role_missing_admin@example.com")
    token = await _login(client, "role_missing_admin@example.com")

    response = await client.patch(
        "/api/v1/users/99999/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": UserRole.MODERATOR.value},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_profile_same_email_skips_duplicate_check(client):
    await register_user(client, "same_email", "same_email@example.com")
    token = await login_user(client, "same_email@example.com")

    response = await client.put(
        "/api/v1/users/me",
        headers=auth_header(token),
        json={"email": "same_email@example.com", "username": "same_email_renamed"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "same_email_renamed"
