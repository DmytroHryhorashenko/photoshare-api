import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import async_session_maker, engine
from app.dependencies import get_db
from app.main import app

TRUNCATE_TABLES_SQL = text(
    """
    TRUNCATE TABLE
        token_blacklist,
        transformed_photos,
        ratings,
        comments,
        photo_tags,
        tags,
        photos,
        users
    RESTART IDENTITY CASCADE
    """
)


async def _truncate_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.execute(TRUNCATE_TABLES_SQL)


@pytest.fixture
async def clean_db():
    """Remove all application data and reset identity sequences before each test."""
    try:
        await _truncate_all_tables()
    except Exception as exc:
        pytest.skip(f"Database not available for integration tests: {exc}")


@pytest.fixture
async def db_session(clean_db):
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Async HTTP client with database session override for integration tests."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def http_client():
    """HTTP client without database override (health checks)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
