from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from tests.helpers import auth_header, login_user, register_user

def test_hash_and_verify_password():
    hashed = hash_password("securepassword123")
    assert hashed != "securepassword123"
    assert verify_password("securepassword123", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_access_token():
    token = create_access_token(
        data={"sub": "1", "role": "user"},
        expires_delta=timedelta(minutes=30),
    )
    payload = decode_access_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_decode_invalid_token_raises():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token("not-a-valid-token")


@pytest.mark.asyncio
async def test_register_login_and_me(client):
    register_payload = {
        "username": "testuser_auth",
        "email": "testuser_auth@example.com",
        "password": "securepassword123",
    }

    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["username"] == register_payload["username"]
    assert user_data["email"] == register_payload["email"]
    assert "password" not in user_data

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == register_payload["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_400(client):
    payload = {
        "username": "duplicate_email_user",
        "email": "duplicate@example.com",
        "password": "securepassword123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    duplicate = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "another_username",
            "email": "duplicate@example.com",
            "password": "securepassword123",
        },
    )
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_duplicate_username_returns_400(client):
    first = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "same_username",
            "email": "first_username@example.com",
            "password": "securepassword123",
        },
    )
    assert first.status_code == 201

    duplicate = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "same_username",
            "email": "second_username@example.com",
            "password": "securepassword123",
        },
    )
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Username already taken"


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_logout_endpoint(client):
    await register_user(client, "auth_logout", "auth_logout@example.com")
    token = await login_user(client, "auth_logout@example.com")
    response = await client.post("/api/v1/auth/logout", headers=auth_header(token))
    assert response.status_code == 204
