"""Repository layer tests."""

import pytest

from app.models.comment import Comment
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.user import User, UserRole
from app.repository.comments import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_photo_comments,
    update_comment,
)
from app.repository.photos import (
    attach_tags_to_photo,
    create_photo,
    create_transformed_photo,
    delete_photo,
    get_or_create_tags,
    get_photo_by_id,
    get_photo_detail,
    get_photo_transformed_links,
    get_transformed_photo_by_id,
    get_user_photo_by_id,
    search_photos,
    update_photo,
)
from app.repository.ratings import (
    create_rating,
    delete_rating,
    get_photo_average_rating,
    get_photo_ratings,
    get_rating_by_id,
    get_user_rating_for_photo,
)
from app.repository.users import (
    count_user_photos,
    count_users,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    set_user_active_status,
    set_user_role,
    update_user,
)


async def _seed_user(db_session, username: str, email: str) -> User:
    return await create_user(
        db_session,
        {
            "username": username,
            "email": email,
            "password_hash": "hashed",
            "role": UserRole.USER,
            "is_active": True,
        },
    )


@pytest.mark.asyncio
async def test_user_repository_crud(db_session):
    user = await _seed_user(db_session, "repo_user", "repo@example.com")
    await db_session.commit()

    assert await get_user_by_email(db_session, "repo@example.com") is not None
    assert await get_user_by_username(db_session, "repo_user") is not None
    assert await get_user_by_id(db_session, user.id) is not None
    assert await count_users(db_session) >= 1

    updated = await update_user(db_session, user, {"username": "repo_updated"})
    assert updated.username == "repo_updated"

    banned = await set_user_active_status(db_session, user.id, False)
    assert banned is not None
    assert banned.is_active is False

    promoted = await set_user_role(db_session, user.id, UserRole.MODERATOR)
    assert promoted is not None
    assert promoted.role == UserRole.MODERATOR

    assert await set_user_active_status(db_session, 99999, True) is None
    assert await set_user_role(db_session, 99999, UserRole.ADMIN) is None


@pytest.mark.asyncio
async def test_photo_repository_crud(db_session):
    user = await _seed_user(db_session, "photo_repo", "photo_repo@example.com")
    await db_session.flush()

    photo = await create_photo(
        db_session,
        user_id=user.id,
        description="Repo photo",
        image_url="https://example.com/a.jpg",
        public_id="repo-photo-1",
    )
    await db_session.commit()

    assert await get_photo_by_id(db_session, photo.id) is not None
    assert await get_photo_by_id(db_session, 99999) is None
    assert await get_user_photo_by_id(db_session, photo.id, user.id) is not None
    assert await get_user_photo_by_id(db_session, photo.id, 99999) is None
    assert await count_user_photos(db_session, user.id) == 1

    detail = await get_photo_detail(db_session, photo.id)
    assert detail is not None

    updated = await update_photo(db_session, photo, {"description": "Updated"})
    assert updated.description == "Updated"

    results = await search_photos(db_session, keyword="Updated", sort_by="date")
    assert len(results) == 1

    tags = await get_or_create_tags(db_session, ["nature", "city"])
    photo = await attach_tags_to_photo(db_session, photo, tags)
    await db_session.commit()

    transform = await create_transformed_photo(
        db_session,
        photo_id=photo.id,
        transformation_type="w100",
        transformed_url="https://example.com/t.jpg",
        qr_code_url="https://example.com/qr.png",
    )
    await db_session.commit()

    assert await get_transformed_photo_by_id(db_session, transform.id) is not None
    links = await get_photo_transformed_links(db_session, photo.id)
    assert len(links) == 1

    await delete_photo(db_session, photo)
    await db_session.commit()
    assert await get_photo_by_id(db_session, photo.id) is None


@pytest.mark.asyncio
async def test_comment_repository_crud(db_session):
    user = await _seed_user(db_session, "comment_repo", "comment_repo@example.com")
    photo = await create_photo(
        db_session,
        user_id=user.id,
        description="Comment target",
        image_url="https://example.com/b.jpg",
        public_id="repo-photo-2",
    )
    await db_session.commit()

    comment = await create_comment(
        db_session,
        photo_id=photo.id,
        user_id=user.id,
        text="Hello",
    )
    await db_session.commit()

    fetched = await get_comment_by_id(db_session, comment.id)
    assert fetched is not None
    comments = await get_photo_comments(db_session, photo.id)
    assert len(comments) == 1

    updated = await update_comment(db_session, comment, "Updated text")
    assert updated.text == "Updated text"

    await delete_comment(db_session, comment)
    await db_session.commit()
    assert await get_comment_by_id(db_session, comment.id) is None


@pytest.mark.asyncio
async def test_rating_repository_crud(db_session):
    owner = await _seed_user(db_session, "rating_owner", "rating_owner@example.com")
    rater = await _seed_user(db_session, "rating_rater", "rating_rater@example.com")
    photo = await create_photo(
        db_session,
        user_id=owner.id,
        description="Rating target",
        image_url="https://example.com/c.jpg",
        public_id="repo-photo-3",
    )
    await db_session.commit()

    rating = await create_rating(
        db_session,
        photo_id=photo.id,
        user_id=rater.id,
        value=4,
    )
    await db_session.commit()

    assert await get_rating_by_id(db_session, rating.id) is not None
    assert await get_user_rating_for_photo(db_session, photo.id, rater.id) is not None
    ratings = await get_photo_ratings(db_session, photo.id)
    assert len(ratings) == 1

    average, count = await get_photo_average_rating(db_session, photo.id)
    assert average == 4.0
    assert count == 1

    await delete_rating(db_session, rating)
    await db_session.commit()
    assert await get_rating_by_id(db_session, rating.id) is None


@pytest.mark.asyncio
async def test_get_or_create_tags_reuses_existing(db_session):
    tag = Tag(name="unique-tag")
    db_session.add(tag)
    await db_session.flush()

    tags = await get_or_create_tags(db_session, ["unique-tag", "new-tag"])
    assert len(tags) == 2
    names = {t.name for t in tags}
    assert names == {"unique-tag", "new-tag"}


@pytest.mark.asyncio
async def test_search_photos_with_filters(db_session):
    from app.models.rating import Rating

    owner = await _seed_user(db_session, "search_filters", "search_filters@example.com")
    rater = await _seed_user(db_session, "search_rater", "search_rater@example.com")
    photo = await create_photo(
        db_session,
        user_id=owner.id,
        description="Filtered photo",
        image_url="https://example.com/f.jpg",
        public_id="filter-photo",
    )
    tags = await get_or_create_tags(db_session, ["filter-tag"])
    await attach_tags_to_photo(db_session, photo, tags)
    db_session.add(Rating(photo_id=photo.id, user_id=rater.id, value=5))
    await db_session.commit()

    by_tag = await search_photos(db_session, tag="filter-tag")
    assert len(by_tag) == 1

    by_rating = await search_photos(db_session, min_rating=4, sort_by="rating", order="asc")
    assert len(by_rating) >= 1

    by_date_asc = await search_photos(db_session, sort_by="date", order="asc")
    assert len(by_date_asc) >= 1

    by_user = await search_photos(db_session, user_id=owner.id)
    assert len(by_user) == 1

    assert await get_user_photo_by_id(db_session, photo.id, owner.id) is not None
