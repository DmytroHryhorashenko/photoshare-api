from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api import auth, comments, photos, ratings, search, transforms, users
from app.config import settings

API_DESCRIPTION = """
PhotoShare is a production-ready REST API for sharing and managing photos.

## Features
- JWT authentication with role-based access control
- Photo upload to Cloudinary with tags (max 5)
- Image transformations with QR code links
- Comments, ratings, and advanced search/filtering
- User profiles with admin ban/unban and role management

## Authentication
Use `POST /api/v1/auth/login` to obtain a JWT, then click **Authorize** and paste:
`Bearer <your_access_token>`
"""

OPENAPI_TAGS = [
    {"name": "health", "description": "Service health checks"},
    {"name": "auth", "description": "Registration, login, logout, and JWT token management"},
    {"name": "users", "description": "User profiles, admin ban/unban, and role management"},
    {"name": "photos", "description": "Photo upload, detail, update, and delete"},
    {"name": "search", "description": "Search and filter photos by keyword, tag, and rating"},
    {"name": "comments", "description": "Photo comments"},
    {"name": "ratings", "description": "Photo ratings (1–5 stars)"},
    {"name": "transforms", "description": "Cloudinary image transformations and QR codes"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="PhotoShare API",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
    contact={
        "name": "PhotoShare API",
    },
    license_info={
        "name": "MIT",
    },
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": (
            "JWT access token from POST /api/v1/auth/login. "
            "Format: Bearer <token>"
        ),
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(search.router, prefix="/api/v1/photos", tags=["search"])
app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])
app.include_router(comments.router, prefix="/api/v1", tags=["comments"])
app.include_router(ratings.router, prefix="/api/v1", tags=["ratings"])
app.include_router(transforms.router, prefix="/api/v1", tags=["transforms"])


@app.get("/", tags=["health"], summary="Root health check")
async def root() -> dict[str, str]:
    return {
        "status": "ok",
        "application": "PhotoShare API",
    }


@app.get("/health", tags=["health"], summary="Liveness health check")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
