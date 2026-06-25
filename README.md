# 🏆 Leaderboard API

> **High-performance async leaderboard service** built with FastAPI, PostgreSQL, Redis and Docker.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-4CAF50?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-4CAF50?style=for-the-badge)](https://coverage.readthedocs.io/)

---

## 🚀 Quick Start (Docker)

The easiest way to run the project is using Docker Compose. No local Python or Database installation required!

### 1. Clone & Configure

```bash
git clone https://github.com/utyara3/LeaderboardAPI.git
cd LeaderboardAPI

# Create environment file from template
cp .env.example .env

# Edit .env with your preferred values (optional for local testing)
# nano .env 
```

### 2. Run
```bash
docker compose up --build
```

### 3. Access
- **Frontend UI:** [http://localhost:8000/](http://localhost:8000/)
- **API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database:** Available at `localhost:5433` (User/Pass defined in `.env`)
- **Redis:** Available at `localhost:6379`

To stop the services:
```bash
docker compose down
```

---

## ## ✨ Features

- 🔐 **Secure Authentication:** JWT-based auth with refresh token rotation and logout functionality.
- ⚡ **Async Architecture:** Built on FastAPI and SQLAlchemy 2.0 (async) for high concurrency.
- 📊 **Dynamic Leaderboards:** Flexible JSONB schema allows custom fields for different game types (e.g., time trials vs. high scores).
- 🔄 **Smart Updates:** Optimistic locking ensures entries are only updated if the new score is better.
- 🛡️ **Rate Limiting:** Redis-based protection against API abuse with configurable limits per endpoint.
- 🧪 **Well-Tested:** Comprehensive test suite with 85% code coverage using pytest.
- 🎨 **Simple Frontend:** Minimal HTML/JS interface for easy testing and demonstration.
- 🐳 **Production-Ready Docker:** Fully containerized setup with automatic migrations via Alembic.

---

## 🛠️ Tech Stack

| Category                  | Technology                      |
| ------------------------- | ------------------------------- |
| **Framework**             | FastAPI                         |
| **Database**              | PostgreSQL 15 + asyncpg         |
| **Cache & Rate Limiting** | Redis 7                         |
| **ORM**                   | SQLAlchemy 2.0 (AsyncIO)        |
| **Migrations**            | Alembic                         |
| **Validation**            | Pydantic v2                     |
| **Testing**               | pytest + pytest-asyncio + httpx |
| **Package Manager**       | uv                              |
| **Containerization**      | Docker & Docker Compose         |

---
## 📂 Project Structure

```
.
├── alembic/                # Database migrations
├── frontend/               # Simple HTML/JS frontend
├── src/
│   ├── api/                # Route handlers (Auth, Leaderboards)
│   ├── auth/               # Authentication utilities and dependencies
│   ├── core/               # Core components (config, database, redis)
│   ├── middleware/         # Rate limiting middleware
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic validation schemas
│   ├── services/           # Business logic layer
│   └── main.py             # Application entry point
├── tests/                  # Test suite (pytest)
├── docker-compose.yml      # Orchestration config
├── Dockerfile              # Image build instructions
├── .env.example            # Environment template
└── README.md
```

---

## 📡 API Endpoints

### Authentication

|Method|Endpoint|Description|
|---|---|---|
|POST|`/auth/register`|Register new user|
|POST|`/auth/login`|Login and get JWT tokens|
|POST|`/auth/refresh`|Refresh access token|
|POST|`/auth/logout`|Logout and revoke refresh token|

### Leaderboards

|Method|Endpoint|Description|
|---|---|---|
|GET|`/leaderboards/`|List all leaderboards (paginated)|
|POST|`/leaderboards/`|Create new leaderboard (auth required)|
|GET|`/leaderboards/{slug}`|Get leaderboard details|
|PUT|`/leaderboards/{slug}`|Update leaderboard (owner only)|
|DELETE|`/leaderboards/{slug}`|Delete leaderboard (owner only)|
|POST|`/leaderboards/{slug}/submit`|Submit score|
|GET|`/leaderboards/{slug}/top`|Get top entries (paginated)|
|GET|`/leaderboards/{slug}/player/{player_id}`|Get player entry|

---

## 🧪 Testing

Run the test suite with coverage report:
```
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 🛡️ Rate Limiting

The API includes Redis-based rate limiting to prevent abuse:

|Endpoint|Limit|Window|
|---|---|---|
|`/auth/login`, `/auth/register`|5 requests|60 seconds|
|`/auth/refresh`|10 requests|60 seconds|
|`/leaderboards/*/submit`|30 requests|60 seconds|
|Other endpoints|100 requests|60 seconds|

Limits are configurable via environment variables.

---

## 🧪 Local Development (Without Docker)

If you prefer running locally:

1. **Install dependencies:** `uv sync`
2. **Set up Database:** Ensure PostgreSQL and Redis are running. Update `.env` with your local credentials.
3. **Run Migrations:** `alembic upgrade head`
4. **Start Server:** `uvicorn src.main:app --reload`

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

<p align="center"> <em>Built with ❤️ by utyara3</em> </p>

