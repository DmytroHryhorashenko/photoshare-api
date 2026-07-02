from datetime import datetime, timedelta, timezone

import pytest

from app.models.photo import Photo
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.user import User, UserRole
from app.repository.photos import search_photos
from app.repository.users import set_user_role
from app.utils.tags import normalize_tag_name


def test_normalize_tag_name_for_search():
    assert normalize_tag_name("  Nature ") == "nature"


async def _seed_search_data(db_session):
    owner = User(
        username="search_owner",
        email="search_owner@example.com",
        password_hash="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    other = User(
        username="search_other",
        email="search_other@example.com",
        password_hash="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add_all([owner, other])
    await db_session.flush()

    nature_tag = Tag(name="nature")
    city_tag = Tag(name="city")
    db_session.add_all([nature_tag, city_tag])
    await db_session.flush()

    now = datetime.now(timezone.utc)
    photo_one = Photo(
        user_id=owner.id,
        description="Beautiful mountain sunset",
        image_url="https://example.com/1.jpg",
        public_id="search-photo-1",
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
    )
    photo_two = Photo(
        user_id=owner.id,
        description="City skyline at night",
        image_url="https://example.com/2.jpg",
        public_id="search-photo-2",
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
    )
    photo_three = Photo(
        user_id=other.id,
        description="Forest trail in nature",
        image_url="https://example.com/3.jpg",
        public_id="search-photo-3",
        created_at=now,
        updated_at=now,
    )
    photo_one.tags = [nature_tag]
    photo_two.tags = [city_tag]
    photo_three.tags = [nature_tag]
    db_session.add_all([photo_one, photo_two, photo_three])
    await db_session.flush()

    db_session.add_all(
        [
            Rating(photo_id=photo_one.id, user_id=other.id, value=5),
            Rating(photo_id=photo_two.id, user_id=other.id, value=3),
            Rating(photo_id=photo_three.id, user_id=owner.id, value=4),
        ]
    )
    await db_session.flush()

    return {
        "owner": owner,
        "other": other,
        "photos": [photo_one, photo_two, photo_three],
    }


@pytest.mark.asyncio
async def test_search_by_keyword(db_session):
    await _seed_search_data(db_session)
    results = await search_photos(db_session, keyword="mountain")
    assert len(results) == 1
    assert "mountain" in (results[0].description or "").lower()


@pytest.mark.asyncio
async def test_search_by_tag(db_session):
    await _seed_search_data(db_session)
    results = await search_photos(db_session, tag="nature")
    assert len(results) == 2
    assert all(any(tag.name == "nature" for tag in photo.tags) for photo in results)


@pytest.mark.asyncio
async def test_filter_by_min_rating(db_session):
    await _seed_search_data(db_session)
    results = await search_photos(db_session, min_rating=4)
    assert len(results) == 2
    assert {photo.public_id for photo in results} == {"search-photo-1", "search-photo-3"}


@pytest.mark.asyncio
async def test_sort_by_date_desc(db_session):
    await _seed_search_data(db_session)
    results = await search_photos(db_session, sort_by="date", order="desc")
    assert [photo.public_id for photo in results] == [
        "search-photo-3",
        "search-photo-2",
        "search-photo-1",
    ]


@pytest.mark.asyncio
async def test_sort_by_rating_desc(db_session):
    await _seed_search_data(db_session)
    results = await search_photos(db_session, sort_by="rating", order="desc")
    assert [photo.public_id for photo in results][:2] == ["search-photo-1", "search-photo-3"]


@pytest.mark.asyncio
async def test_reject_user_id_filter_for_normal_user(client, db_session):
    data = await _seed_search_data(db_session)
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "search_normal",
            "email": "search_normal@example.com",
            "password": "securepassword123",
        },
    )
    token = (
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": "search_normal@example.com",
                "password": "securepassword123",
            },
        )
    ).json()["access_token"]

    response = await client.get(
        "/api/v1/photos/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"user_id": data["owner"].id},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_allow_user_id_filter_for_moderator(client, db_session):
    data = await _seed_search_data(db_session)
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "search_mod",
            "email": "search_mod@example.com",
            "password": "securepassword123",
        },
    )
    mod_id = register_response.json()["id"]
    await set_user_role(db_session, mod_id, UserRole.MODERATOR)

    token = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": "search_mod@example.com", "password": "securepassword123"},
        )
    ).json()["access_token"]

    response = await client.get(
        "/api/v1/photos/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"user_id": data["owner"].id},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(item["user_id"] == data["owner"].id for item in response.json())


@pytest.mark.asyncio
async def test_search_invalid_sort_by(client):
    response = await client.get("/api/v1/photos/search", params={"sort_by": "invalid"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_search_invalid_order(client):
    response = await client.get("/api/v1/photos/search", params={"order": "sideways"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_search_invalid_min_rating(client):
    response = await client.get("/api/v1/photos/search", params={"min_rating": 0})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_invalid_tag(client):
    response = await client.get("/api/v1/photos/search", params={"tag": "   "})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_search_api_returns_results(client, db_session):
    from tests.test_search import _seed_search_data

    await _seed_search_data(db_session)
    await db_session.commit()

    response = await client.get("/api/v1/photos/search", params={"keyword": "mountain"})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_allow_user_id_filter_for_admin(client, db_session):
    data = await _seed_search_data(db_session)
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "search_admin",
            "email": "search_admin@example.com",
            "password": "securepassword123",
        },
    )
    admin_id = register_response.json()["id"]
    await set_user_role(db_session, admin_id, UserRole.ADMIN)

    token = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": "search_admin@example.com", "password": "securepassword123"},
        )
    ).json()["access_token"]

    response = await client.get(
        "/api/v1/photos/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"user_id": data["owner"].id},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
