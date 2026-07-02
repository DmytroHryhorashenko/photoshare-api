"""Dependency and permission integration tests."""

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.permissions import require_owner_or_admin
from app.core.security import create_access_token
from app.main import app
from tests.helpers import auth_header, login_user, register_user


def test_custom_openapi_schema_is_cached():
    schema_first = app.openapi()
    schema_second = app.openapi()
    assert schema_first is schema_second
    assert "BearerAuth" in schema_first["components"]["securitySchemes"]


@pytest.mark.asyncio
async def test_get_me_requires_valid_token(client):
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_rejects_token_without_subject(client):
    token = create_access_token(data={"role": "user"}, expires_delta=timedelta(minutes=5))
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_header(token),
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_blacklists_token(client):
    await register_user(client, "logout_api", "logout_api@example.com")
    token = await login_user(client, "logout_api@example.com")

    logout_response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_header(token),
    )
    assert logout_response.status_code == 204

    me_response = await client.get(
        "/api/v1/users/me",
        headers=auth_header(token),
    )
    assert me_response.status_code == 401


@pytest.mark.asyncio
async def test_search_with_invalid_token_ignores_auth(client):
    response = await client.get(
        "/api/v1/photos/search",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_me_rejects_blacklisted_token(client):
    await register_user(client, "blacklist_me", "blacklist_me@example.com")
    token = await login_user(client, "blacklist_me@example.com")
    await client.post("/api/v1/auth/logout", headers=auth_header(token))

    response = await client.get("/api/v1/users/me", headers=auth_header(token))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_rejects_token_for_missing_user(client, db_session):
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    user = User(
        username="ghost",
        email="ghost@example.com",
        password_hash=hash_password("securepassword123"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=5),
    )
    await db_session.delete(user)
    await db_session.commit()

    response = await client.get("/api/v1/users/me", headers=auth_header(token))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_require_owner_or_admin_denies_other_user():
    from app.models.user import User, UserRole

    checker = require_owner_or_admin(1)
    other = User(
        id=2,
        username="other",
        email="other@example.com",
        password_hash="hashed",
        role=UserRole.USER,
        is_active=True,
    )

    with pytest.raises(HTTPException) as exc:
        await checker(current_user=other)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_db_closes_session():
    from app.dependencies import get_db

    sessions = []
    async for session in get_db():
        sessions.append(session)
    assert len(sessions) == 1
    assert sessions[0] is not None


@pytest.mark.asyncio
async def test_optional_user_returns_none_for_blacklisted_token(client):
    await register_user(client, "opt_blacklist", "opt_blacklist@example.com")
    token = await login_user(client, "opt_blacklist@example.com")
    await client.post("/api/v1/auth/logout", headers=auth_header(token))

    response = await client.get(
        "/api/v1/photos/search",
        headers=auth_header(token),
        params={"user_id": 1},
    )
    # Blacklisted token is ignored; unauthenticated user_id filter is forbidden.
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_optional_user_returns_none_for_token_without_subject(client):
    token = create_access_token(data={"role": "user"}, expires_delta=timedelta(minutes=5))
    response = await client.get(
        "/api/v1/photos/search",
        headers=auth_header(token),
        params={"user_id": 1},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_require_owner_or_admin_allows_admin():
    from app.models.user import User, UserRole

    checker = require_owner_or_admin(1)
    admin = User(
        id=99,
        username="admin",
        email="admin@example.com",
        password_hash="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    result = await checker(current_user=admin)
    assert result.id == 99
