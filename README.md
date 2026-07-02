# 📸 PhotoShare API

**PhotoShare API** — production-ready REST API для обміну та керування фотографіями. Користувачі можуть завантажувати зображення в Cloudinary, додавати теги, оцінювати та коментувати фото, застосовувати трансформації з QR-кодами та виконувати розширений пошук із фільтрами.

Проєкт побудований на **FastAPI**, **SQLAlchemy 2.0 (async)**, **PostgreSQL**, **JWT-автентифікації** та **Docker**. Основним deliverable є REST API; Swagger UI дозволяє повністю перевірити функціонал без frontend.

---

# 🚀 Основні можливості

| Можливість | Опис |
|------------|------|
| ✅ JWT Authentication | Реєстрація, вхід, вихід із чорним списком токенів |
| ✅ User Roles (User / Moderator / Admin) | Рольова модель доступу; перший користувач стає адміністратором |
| ✅ Registration / Login / Logout | Повний цикл автентифікації через JWT |
| ✅ User Profiles | Приватний профіль `/me` та публічні профілі з кількістю фото |
| ✅ Ban / Unban | Адміністратор може блокувати та розблоковувати користувачів |
| ✅ Photo Upload | Завантаження зображень (multipart) з валідацією типу файлу |
| ✅ CRUD Photos | Створення, читання, оновлення та видалення фотографій |
| ✅ Cloudinary Integration | Зберігання медіа, трансформації та QR-коди в хмарі |
| ✅ Image Transformations | Зміна розміру, кадрування, ефекти (grayscale, sepia тощо) |
| ✅ QR Code generation | Генерація QR-посилань на трансформовані зображення |
| ✅ Comments | Коментарі до фото; редагування — лише власником |
| ✅ Ratings | Оцінки від 1 до 5 зірок; одна оцінка на користувача на фото |
| ✅ Search & Filtering | Пошук за ключовим словом, тегом, мінімальним рейтингом, сортування |
| ✅ PostgreSQL | Реляційна база даних PostgreSQL 16 |
| ✅ SQLAlchemy 2.0 | Асинхронний ORM із сучасним API |
| ✅ Alembic | Версіонування та застосування міграцій схеми БД |
| ✅ Docker | Контейнеризація API-сервісу |
| ✅ Docker Compose | Оркестрація API, PostgreSQL та опційного frontend |
| ✅ Swagger | Інтерактивна OpenAPI-документація |
| ✅ Unit & Integration Tests | 184 тести, покриття коду 94% |

**Додаткові деталі:**

- До **5 тегів** на одне фото; теги створюються автоматично при завантаженні
- Коментарі: редагування — власником; видалення — модератором/адміном
- Оцінки: заборона оцінювати власне фото та дублювання оцінок
- Трансформації: доступні власнику фото та адміністратору
- Пошук: фільтр `user_id` — лише для модератора та адміністратора

---

# 🛠 Використані технології

| Категорія | Технологія | Призначення |
|-----------|------------|-------------|
| Мова | **Python 3.13+** | Backend runtime |
| Framework | **FastAPI** | REST API, валідація, OpenAPI |
| База даних | **PostgreSQL 16** | Зберігання даних |
| ORM | **SQLAlchemy 2.0** | Асинхронна робота з БД |
| Міграції | **Alembic** | Версіонування схеми БД |
| Валідація | **Pydantic v2** | DTO та схеми запитів/відповідей |
| Контейнеризація | **Docker** | Ізоляція середовища |
| Оркестрація | **Docker Compose** | Запуск повного стеку |
| Автентифікація | **JWT** (python-jose + bcrypt/passlib) | Токени доступу |
| Медіа | **Cloudinary** | Зберігання та трансформація зображень |
| QR-коди | **qrcode**, **Pillow** | Генерація QR-зображень |
| Тестування | **Pytest**, **pytest-cov** | Unit та integration тести |
| Frontend (опційно) | **React**, **Vite**, **TypeScript** | Візуальна демонстрація |
| Стилізація frontend | **Tailwind CSS** | UI компоненти |

---

# 📂 Структура проєкту

```
photoshare-api/
├── app/
│   ├── main.py              # Точка входу FastAPI
│   ├── config.py            # Налаштування з .env
│   ├── database.py          # Підключення до БД (async)
│   ├── dependencies.py      # DI: auth, DB session
│   ├── api/                 # HTTP-роути (auth, users, photos, …)
│   ├── core/                # Безпека (JWT), permissions
│   ├── models/              # SQLAlchemy ORM-моделі
│   ├── schemas/             # Pydantic DTO
│   ├── repository/          # Шар доступу до даних
│   ├── services/            # Бізнес-логіка (auth, cloudinary, qr)
│   └── utils/               # Допоміжні функції
├── alembic/                 # Міграції Alembic
│   └── versions/
├── tests/                   # Unit та integration тести
│   ├── conftest.py          # Фікстури pytest (ізоляція БД)
│   ├── helpers.py           # Спільні хелпери для тестів
│   └── test_*.py            # Тестові модулі
├── frontend/                # Опційний React frontend (Vite + TS)
│   ├── src/
│   │   ├── api/             # HTTP-клієнт до API
│   │   ├── components/      # UI-компоненти
│   │   ├── context/         # AuthContext
│   │   └── pages/           # Сторінки (Gallery, Upload, Admin, …)
│   └── Dockerfile
├── scripts/
│   └── docker-entrypoint.sh # Міграції + запуск API в Docker
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── alembic.ini
├── .coveragerc
├── LICENSE
├── .env.example
└── README.md
```

**Архітектура шарів:**

```
API (routers) → Services → Repository → Models (ORM)
                    ↓
                Schemas (Pydantic)
```

---

# ⚙️ Встановлення

## Варіант 1: Docker (рекомендовано)

### Крок 1 — Клонування репозиторію

```bash
git clone https://github.com/DmytroHryhorashenko/photoshare-api.git
cd photoshare-api
```

### Крок 2 — Налаштування змінних середовища

```bash
cp .env.example .env
```

Відредагуйте `.env`: встановіть `SECRET_KEY` та облікові дані Cloudinary (див. розділ [🔑 Змінні середовища](#-змінні-середовища)).

### Крок 3 — Запуск стеку

```bash
docker compose up -d --build
```

> **Примітка:** поточний `docker-compose.yml` налаштований для **локальної розробки** (`--reload`, bind-mount `.:/app`). Для production використовуйте окремий compose-файл або платформу розгортання (Koyeb, Fly.io) без bind-mount і hot-reload.

Міграції Alembic виконуються автоматично при старті контейнера через `scripts/docker-entrypoint.sh`.

### Крок 4 — Перевірка

| Сервіс | URL |
|--------|-----|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Frontend (опційно) | http://localhost:5173 |
| PostgreSQL | `localhost:5432` |

Зупинка стеку:

```bash
docker compose down
```

Повне видалення томів (очищення БД):

```bash
docker compose down -v
```

---

## Варіант 2: Локальне встановлення (без Docker)

### Передумови

- Python 3.13+
- PostgreSQL 16+ (або лише БД в Docker)
- Обліковий запис Cloudinary (для завантаження фото)

### Кроки

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Застосуйте міграції та запустіть сервер:

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Перевірка health check:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

---

# 🔑 Змінні середовища

Скопіюйте `.env.example` у `.env` і налаштуйте значення перед запуском.

| Змінна | Обов'язкова | Опис |
|--------|:-----------:|------|
| `APP_ENV` | Ні | Середовище: `development` або `production` (за замовчуванням: `development`) |
| `DEBUG` | Ні | Режим відладки та SQL echo (за замовчуванням: `false`) |
| `DATABASE_URL` | **Так** | Async URL PostgreSQL: `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | **Так** | Секретний ключ для підпису JWT (мінімум 32 випадкових символів) |
| `ALGORITHM` | Ні | Алгоритм JWT (за замовчуванням: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Ні | Час життя токена в хвилинах (за замовчуванням: `30`) |
| `CLOUDINARY_NAME` | **Так*** | Cloud name вашого Cloudinary-акаунту |
| `CLOUDINARY_API_KEY` | **Так*** | API Key Cloudinary |
| `CLOUDINARY_API_SECRET` | **Так*** | API Secret Cloudinary |

\* **Обов'язкові** для завантаження фото, трансформацій зображень та генерації QR-кодів.

**Приклад `DATABASE_URL` для локальної розробки:**

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/photoshare
```

**У Docker Compose** змінна `DATABASE_URL` перевизначається автоматично для підключення до сервісу `db`:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/photoshare
```

> **Безпека:** ніколи не комітьте `.env` у Git. У production використовуйте сильний `SECRET_KEY` та змінні середовища платформи розгортання.

---

# ▶️ Запуск проєкту

## Docker Compose (повний стек)

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f api
```

## Локальний запуск API

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Опційний frontend (локально, без Docker)

```bash
cd frontend
npm install
npm run dev
```

За потреби вкажіть URL API у `frontend/.env`:

```
VITE_API_URL=http://localhost:8000/api/v1
```

## Корисні команди Docker

```bash
# Перезапуск API
docker compose restart api

# Виконання команди всередині контейнера API
docker compose exec api bash

# Перегляд логів
docker compose logs api
```

---

# 🗄 Міграції Alembic

| Команда | Опис |
|---------|------|
| `alembic revision --autogenerate -m "description"` | Створити міграцію на основі змін моделей |
| `alembic upgrade head` | Застосувати всі очікувані міграції |
| `alembic downgrade -1` | Відкотити останню міграцію |
| `alembic history` | Переглянути історію міграцій |
| `alembic current` | Поточна ревізія БД |

**У Docker:**

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic current
docker compose exec api alembic history
```

> При старті через Docker міграції виконуються автоматично в `scripts/docker-entrypoint.sh`.

---

# 🧪 Тестування

Проєкт містить **184** unit та integration тести з **ізольованою тестовою БД** (очищення таблиць перед кожним тестом). Cloudinary та QR-сервіси **мокуються** — реальні зовнішні виклики не виконуються.

## Локально

```bash
# Усі тести (verbose)
pytest -v

# З покриттям коду
pytest --cov=app --cov-report=term-missing

# HTML-звіт покриття
pytest --cov=app --cov-report=html
```

## У Docker (рекомендовано)

```bash
docker compose exec api pytest -v
docker compose exec api pytest --cov=app --cov-report=term-missing -v
```

## Результати

| Показник | Значення |
|----------|----------|
| ✅ Тестів пройдено | **184** |
| ✅ Покриття коду | **94%** |
| ✅ Пропущених тестів | **0** |

---

# 📖 Swagger

Інтерактивна документація OpenAPI — **основний інструмент перевірки** для ментора та розробника. Через Swagger можна повністю верифікувати REST API без frontend.

| Ресурс | URL |
|--------|-----|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |
| Health check | http://localhost:8000/health |
| Root | http://localhost:8000/ |

**Як авторизуватися в Swagger:**

1. Виконайте `POST /api/v1/auth/login` — отримайте `access_token`
2. Натисніть **Authorize** у Swagger UI
3. Введіть: `Bearer <your_access_token>`

**Базовий URL API:** `http://localhost:8000/api/v1`

### Огляд ендпоінтів

#### Auth (`/auth`)

| Method | Endpoint | Доступ | Опис |
|--------|----------|--------|------|
| POST | `/auth/register` | Public | Реєстрація нового користувача |
| POST | `/auth/login` | Public | Вхід, повертає JWT |
| POST | `/auth/logout` | Authenticated | Додати токен до чорного списку |

#### Users (`/users`)

| Method | Endpoint | Доступ | Опис |
|--------|----------|--------|------|
| GET | `/users/me` | Authenticated | Профіль поточного користувача |
| PUT | `/users/me` | Authenticated | Оновлення username, email, password |
| GET | `/users/{username}` | Public | Публічний профіль + кількість фото |
| PATCH | `/users/{id}/ban` | Admin | Заблокувати користувача |
| PATCH | `/users/{id}/unban` | Admin | Розблокувати користувача |
| PATCH | `/users/{id}/role` | Admin | Змінити роль користувача |

#### Photos (`/photos`)

| Method | Endpoint | Доступ | Опис |
|--------|----------|--------|------|
| POST | `/photos` | Authenticated | Завантаження фото (multipart) |
| GET | `/photos/search` | Public | Пошук та фільтрація |
| GET | `/photos/{id}` | Public | Деталі фото |
| PUT | `/photos/{id}` | Owner/Admin | Оновлення опису та тегів |
| DELETE | `/photos/{id}` | Owner/Admin | Видалення фото |

#### Comments

| Method | Endpoint | Доступ | Опис |
|--------|----------|--------|------|
| POST | `/photos/{id}/comments` | Authenticated | Додати коментар |
| GET | `/photos/{id}/comments` | Public | Список коментарів |
| PUT | `/comments/{id}` | Owner | Редагувати власний коментар |
| DELETE | `/comments/{id}` | Moderator/Admin | Видалити коментар |

#### Ratings

| Method | Endpoint | Доступ | Опис |
|--------|----------|--------|------|
| POST | `/photos/{id}/ratings` | Authenticated | Оцінити фото (1–5) |
| GET | `/photos/{id}/ratings` | Public | Середній рейтинг |
| DELETE | `/ratings/{id}` | Moderator/Admin | Видалити оцінку |

#### Transforms

| Method | Endpoint | Доступ | Опис |
|--------|----------|--------|------|
| POST | `/photos/{id}/transform` | Owner/Admin | Трансформація + QR-код |
| GET | `/photos/{id}/transforms` | Public | Список трансформацій |
| GET | `/transforms/{id}` | Public | Отримати трансформацію |

#### Health

| Method | Endpoint | Опис |
|--------|----------|------|
| GET | `/` | Статус кореневого маршруту |
| GET | `/health` | Liveness check |

---

# 💻 Frontend (Optional)

> **Важливо:** основним deliverable проєкту є **REST API**. Frontend включено лише як **опційну візуальну демонстрацію** і **не замінює** перевірку через Swagger.

| Сервіс | URL |
|--------|-----|
| **API** | http://localhost:8000 |
| **Frontend** | http://localhost:5173 |

### Сторінки frontend

| Сторінка | URL |
|----------|-----|
| Landing | http://localhost:5173 |
| Gallery | http://localhost:5173/gallery |
| Upload | http://localhost:5173/upload |
| Photo Detail | http://localhost:5173/photos/:id |
| Profile | http://localhost:5173/profile/:username |
| Admin | http://localhost:5173/admin |
| Login / Register | http://localhost:5173/login, `/register` |

Посилання на API Docs у frontend відкриває http://localhost:8000/docs.

### Запуск повного стеку

```bash
docker compose up -d --build
docker compose ps
```

---

# 📷 Screenshots

> Додайте знімки екрана у папку `docs/screenshots/` та оновіть шляхи нижче.

### Swagger UI

![Swagger UI — інтерактивна документація API](docs/screenshots/swagger-ui.png)

### Frontend Landing

![Головна сторінка PhotoShare](docs/screenshots/frontend-landing.png)

### Gallery

![Галерея фотографій](docs/screenshots/frontend-gallery.png)

### Profile

![Публічний профіль користувача](docs/screenshots/frontend-profile.png)

### Upload Photo

![Сторінка завантаження фото](docs/screenshots/frontend-upload.png)

### Admin Panel

![Панель адміністратора](docs/screenshots/frontend-admin.png)

---

# 📋 Реалізовані вимоги технічного завдання

## Автентифікація та користувачі

- [x] ✅ Реєстрація користувача (`POST /auth/register`)
- [x] ✅ Вхід з отриманням JWT (`POST /auth/login`)
- [x] ✅ Вихід із чорним списком токенів (`POST /auth/logout`)
- [x] ✅ JWT-автентифікація для захищених маршрутів
- [x] ✅ Ролі: User, Moderator, Admin
- [x] ✅ Перший зареєстрований користувач — Admin
- [x] ✅ Приватний профіль `/users/me`
- [x] ✅ Публічний профіль за username
- [x] ✅ Оновлення профілю (username, email, password)
- [x] ✅ Блокування користувача (ban) — Admin
- [x] ✅ Розблокування користувача (unban) — Admin
- [x] ✅ Зміна ролі користувача — Admin
- [x] ✅ Неактивний користувач не може увійти та отримати доступ

## Фотографії

- [x] ✅ Завантаження фото в Cloudinary (multipart/form-data)
- [x] ✅ Валідація типу файлу (jpeg, png, gif, webp)
- [x] ✅ CRUD операції з фотографіями
- [x] ✅ Теги (до 5 на фото), автоматичне створення
- [x] ✅ Детальна сторінка фото (коментарі, рейтинг, трансформації)
- [x] ✅ Видалення фото з Cloudinary при delete
- [x] ✅ Доступ Owner/Admin для edit/delete

## Коментарі та оцінки

- [x] ✅ Додавання коментарів до фото
- [x] ✅ Редагування власного коментаря
- [x] ✅ Видалення коментарів — Moderator/Admin
- [x] ✅ Оцінка фото (1–5 зірок)
- [x] ✅ Заборона оцінювати власне фото
- [x] ✅ Заборона дублювання оцінки
- [x] ✅ Середній рейтинг та кількість оцінок
- [x] ✅ Видалення оцінок — Moderator/Admin

## Трансформації та QR

- [x] ✅ Трансформації зображень через Cloudinary (width, height, crop, angle, effect, format)
- [x] ✅ Генерація QR-коду з посиланням на трансформоване зображення
- [x] ✅ Збереження історії трансформацій
- [x] ✅ Доступ Owner/Admin для створення трансформацій

## Пошук та фільтрація

- [x] ✅ Пошук за ключовим словом (опис фото)
- [x] ✅ Фільтр за тегом
- [x] ✅ Фільтр за мінімальним рейтингом
- [x] ✅ Сортування за датою або рейтингом (asc/desc)
- [x] ✅ Фільтр за `user_id` — Moderator/Admin

## Інфраструктура та якість

- [x] ✅ PostgreSQL + SQLAlchemy 2.0 (async)
- [x] ✅ Alembic міграції
- [x] ✅ Docker + Docker Compose
- [x] ✅ Swagger / ReDoc / OpenAPI
- [x] ✅ Шарова архітектура (API → Service → Repository)
- [x] ✅ Pydantic v2 валідація
- [x] ✅ Unit та integration тести (184 тести, 94% coverage)
- [x] ✅ Опційний React frontend (візуальна демонстрація)

---

# 📈 Показники проєкту

| Показник | Значення |
|----------|----------|
| **Tests passed** | **184** |
| **Coverage** | **94%** |
| **Docker** | ✅ |
| **Docker Compose** | ✅ |
| **Swagger / OpenAPI** | ✅ |
| **PostgreSQL** | ✅ |
| **Alembic** | ✅ |
| **Cloudinary** | ✅ |
| **JWT Auth** | ✅ |
| **Role-based Access** | ✅ |
| **Frontend** | ✅ Optional |

---

# 🚢 Розгортання (Deployment)

## Koyeb

1. Завантажте репозиторій на GitHub.
2. Створіть застосунок на Koyeb із **Dockerfile**.
3. Підключіть **PostgreSQL** (managed або зовнішню БД).
4. Додайте змінні середовища з `.env.example`.
5. Команда запуску (якщо не використовується CMD Dockerfile):

   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. Відкрийте порт `8000` та задеплойте.

## Fly.io

```bash
fly launch
fly postgres create
fly secrets set SECRET_KEY=... CLOUDINARY_NAME=... CLOUDINARY_API_KEY=... CLOUDINARY_API_SECRET=...
fly secrets set DATABASE_URL=postgresql+asyncpg://...
fly deploy
```

Міграції після деплою:

```bash
fly ssh console -C "alembic upgrade head"
```

## Production — рекомендації

- Встановіть `APP_ENV=production` та `DEBUG=false`
- Використовуйте сильний `SECRET_KEY` (32+ випадкових символів)
- Обмежте CORS origins у `app/main.py` для production
- Використовуйте managed PostgreSQL із SSL
- Зберігайте секрети у змінних середовища платформи, **ніколи в Git**

---

# 📄 Ліцензія

Проєкт розповсюджується під ліцензією **MIT**.

---

# 👨‍💻 Автор

Розроблено як **FastAPI REST API** проєкт у рамках дипломної / навчальної роботи.

Побудовано з використанням сучасної Python backend-архітектури та найкращих практик розробки: шарове розділення відповідальності, асинхронна робота з БД, JWT-автентифікація, контейнеризація, автоматизоване тестування та повна OpenAPI-документація.

**Репозиторій:** [github.com/DmytroHryhorashenko/photoshare-api](https://github.com/DmytroHryhorashenko/photoshare-api)
