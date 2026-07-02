# PhotoShare API

Production-ready REST API for sharing and managing photos. Users can upload images to Cloudinary, tag them, rate and comment, apply transformations with QR codes, and search with advanced filters. Built with **FastAPI**, **SQLAlchemy 2.0 (async)**, **PostgreSQL**, **JWT authentication**, and **Docker**.

## Features

- **JWT authentication** — register, login, logout with token blacklist
- **Role-based access control** — `user`, `moderator`, `admin` (first user becomes admin)
- **User profiles** — private `/me` endpoint and public profiles with photo counts
- **Admin tools** — ban/unban users, change roles
- **Photo management** — upload, update, delete with Cloudinary integration
- **Tags** — up to 5 tags per photo, auto-created on upload
- **Comments** — owner-only edit, moderator/admin delete
- **Ratings** — 1–5 stars, one rating per user per photo
- **Transformations** — Cloudinary resize/crop/effects with QR code links
- **Search & filtering** — keyword, tag, min rating, sort by date or rating

## Tech Stack

| Layer | Technology |
|-------|------------|
| Runtime | Python 3.13+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (Async) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Media | Cloudinary + QR codes (qrcode, Pillow) |
| Containerization | Docker & Docker Compose |
| Testing | Pytest + pytest-cov |

## Quick Start (Docker)

```bash
git clone <repository-url>
cd photoshare-api
cp .env.example .env
# Edit .env — set SECRET_KEY and Cloudinary credentials
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| **Swagger UI** | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 |

Migrations run automatically on container startup via `scripts/docker-entrypoint.sh`.

Stop the stack:

```bash
docker compose down
```

## Installation (Local)

### Prerequisites

- Python 3.13+
- PostgreSQL 16+ (or use Docker for DB only)
- Cloudinary account (for photo upload)

### Steps

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### Environment Variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | No | `development` or `production` (default: `development`) |
| `DEBUG` | No | SQL echo and debug mode (default: `false`) |
| `DATABASE_URL` | Yes | Async PostgreSQL URL: `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Yes | JWT signing secret (use a long random string) |
| `ALGORITHM` | No | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime in minutes (default: `30`) |
| `CLOUDINARY_NAME` | Yes* | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Yes* | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Yes* | Cloudinary API secret |

\* Required for photo upload, transformations, and QR codes.

**Local `DATABASE_URL` example:**

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/photoshare
```

**Docker Compose** overrides `DATABASE_URL` to use the `db` service hostname.

### Run Locally

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/
```

## Alembic Migrations

| Command | Description |
|---------|-------------|
| `alembic revision --autogenerate -m "description"` | Generate migration from model changes |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back last migration |
| `alembic history` | Show migration history |
| `alembic current` | Show current revision |

Inside Docker:

```bash
docker compose exec api alembic upgrade head
```

## Testing

```bash
# Run all tests
pytest -v

# With coverage report
pytest --cov=app --cov-report=term-missing

# HTML coverage report
pytest --cov=app --cov-report=html
```

Inside Docker:

```bash
docker compose exec api pytest --cov=app --cov-report=term-missing -v
```

## API Endpoint Overview

Base URL: `http://localhost:8000/api/v1`

### Auth (`/auth`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register new user |
| POST | `/auth/login` | Public | Login, returns JWT |
| POST | `/auth/logout` | Authenticated | Blacklist current token |

### Users (`/users`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/users/me` | Authenticated | Current user profile |
| PUT | `/users/me` | Authenticated | Update username, email, password |
| GET | `/users/{username}` | Public | Public profile + photo count |
| PATCH | `/users/{id}/ban` | Admin | Ban user |
| PATCH | `/users/{id}/unban` | Admin | Unban user |
| PATCH | `/users/{id}/role` | Admin | Change user role |

### Photos (`/photos`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/photos` | Authenticated | Upload photo (multipart) |
| GET | `/photos/search` | Public | Search and filter photos |
| GET | `/photos/{id}` | Public | Photo detail |
| PUT | `/photos/{id}` | Owner/Admin | Update description and tags |
| DELETE | `/photos/{id}` | Owner/Admin | Delete photo |

### Comments

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/photos/{id}/comments` | Authenticated | Add comment |
| GET | `/photos/{id}/comments` | Public | List comments |
| PUT | `/comments/{id}` | Owner | Edit own comment |
| DELETE | `/comments/{id}` | Moderator/Admin | Delete comment |

### Ratings

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/photos/{id}/ratings` | Authenticated | Rate photo (1–5) |
| GET | `/photos/{id}/ratings` | Public | Average rating summary |
| DELETE | `/ratings/{id}` | Moderator/Admin | Delete rating |

### Transforms

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/photos/{id}/transform` | Owner/Admin | Create transformation + QR |
| GET | `/photos/{id}/transforms` | Public | List transformations |
| GET | `/transforms/{id}` | Public | Get transformation |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root status |
| GET | `/health` | Liveness check |

**Swagger UI:** http://localhost:8000/docs

## Architecture

```
API (routers) → Services → Repository → Models (ORM)
                    ↓
                Schemas (Pydantic)
```

```
photoshare-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── api/           # Route handlers
│   ├── core/          # Security, permissions
│   ├── models/        # SQLAlchemy ORM
│   ├── schemas/       # Pydantic DTOs
│   ├── repository/    # Data access
│   ├── services/      # Business logic
│   └── utils/
├── alembic/
├── tests/
├── scripts/           # Docker entrypoint
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Deployment

### Koyeb

1. Push repository to GitHub.
2. Create a Koyeb app from the GitHub repo using the **Dockerfile**.
3. Add a **PostgreSQL** database (Koyeb managed or external).
4. Set environment variables from `.env.example`.
5. Set the run command (if not using Dockerfile CMD):

   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. Expose port `8000` and deploy.

### Fly.io

```bash
fly launch
fly postgres create
fly secrets set SECRET_KEY=... CLOUDINARY_NAME=... CLOUDINARY_API_KEY=... CLOUDINARY_API_SECRET=...
fly secrets set DATABASE_URL=postgresql+asyncpg://...
fly deploy
```

Run migrations after deploy:

```bash
fly ssh console -C "alembic upgrade head"
```

### Production Notes

- Set `APP_ENV=production` and `DEBUG=false`
- Use a strong `SECRET_KEY` (32+ random characters)
- Restrict CORS origins in `app/main.py` for production
- Use managed PostgreSQL with SSL
- Store secrets in platform environment variables, never in git

## Implementation Checklist

| Feature | Status |
|---------|--------|
| JWT authentication | ✅ |
| User roles (user, moderator, admin) | ✅ |
| User profiles (private + public) | ✅ |
| Ban / unban users | ✅ |
| Photo upload | ✅ |
| Tags (max 5 per photo) | ✅ |
| Cloudinary integration | ✅ |
| Image transformations | ✅ |
| QR code links | ✅ |
| Comments | ✅ |
| Ratings (1–5) | ✅ |
| Search & filtering | ✅ |
| Docker & Docker Compose | ✅ |
| PostgreSQL | ✅ |
| Alembic migrations | ✅ |
| Swagger / OpenAPI docs | ✅ |

## License

MIT
