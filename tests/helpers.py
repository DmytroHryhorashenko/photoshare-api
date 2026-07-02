"""Shared helpers for integration tests."""

import io

from httpx import AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import Photo
from app.models.user import UserRole
from app.repository.users import set_user_role

PASSWORD = "securepassword123"


def make_jpeg_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color="blue").save(buffer, format="JPEG")
    return buffer.getvalue()


async def register_user(
    client: AsyncClient,
    username: str,
    email: str,
    password: str = PASSWORD,
) -> dict:
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str,
    password: str = PASSWORD,
) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def create_photo_in_db(
    db_session: AsyncSession,
    user_id: int,
    *,
    public_id: str = "test-photo",
    description: str = "Test photo",
) -> Photo:
    photo = Photo(
        user_id=user_id,
        description=description,
        image_url="https://example.com/photo.jpg",
        public_id=public_id,
    )
    db_session.add(photo)
    await db_session.flush()
    await db_session.refresh(photo)
    return photo


async def promote_to_moderator(db_session: AsyncSession, user_id: int) -> None:
    await set_user_role(db_session, user_id, UserRole.MODERATOR)
    await db_session.commit()


async def promote_to_admin(db_session: AsyncSession, user_id: int) -> None:
    await set_user_role(db_session, user_id, UserRole.ADMIN)
    await db_session.commit()
