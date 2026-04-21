# 🏆 Leaderboard API

> **High-performance async leaderboard service** built with FastAPI and PostgreSQL
> *Work in Progress — Actively Developed*

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)

---

## 📖 Overview

A production-ready, fully asynchronous leaderboard management system designed for gaming platforms, competitive applications, and real-time ranking scenarios. The service provides flexible schema definitions, efficient ranking calculations using PostgreSQL window functions, and secure JWT-based authentication.

### ✨ Key Features

- 🔐 **JWT Authentication** — Secure user registration, login, and token-based authorization
- 🎯 **Dynamic Schema** — Configurable leaderboard fields via JSONB with runtime type validation
- ⚡ **Real-time Ranking** — Efficient rank calculation using PostgreSQL `RANK()` window functions
- 🔄 **Optimistic Updates** — Smart entry submission that only updates when scores improve
- 📊 **Pagination Support** — Built-in pagination for large leaderboards
- 🛠️ **Async Architecture** — Full async stack with `asyncpg` and SQLAlchemy 2.0

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│                    (REST API Consumer)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Auth Router  │  │ LB Router    │  │ Health Checks    │   │
│  │ /auth/*      │  │ /leaderboards│  │ /health          │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ LeaderboardService                                   │   │
│  │ • create_leaderboard()                               │   │
│  │ • submit_entry()  ← RANK() OVER()                    │   │
│  │ • get_top_entries()                                  │   │
│  │ • validate_values()                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                         │
│         SQLAlchemy 2.0 (AsyncSession + ORM)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                      │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │  users   │  │ leaderboards │  │     entries      │        │
│  │ ─────────│  │ ──────────── │  │ ───────────────  │        │
│  │ id (UUID)│  │ id (UUID)    │  │ id (UUID)        │        │
│  │ username │  │ slug (UK)    │  │ leaderboard_id   │        │
│  │ email    │  │ owner_id     │  │ player_id        │        │
│  │ password │  │ fields_schema│  │ values (JSONB)   │        │
│  └──────────┘  │ sort_field   │  │ rank (computed)  │        │
│                │ sort_order   │  └──────────────────┘        │
│                └──────────────┘                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

| Category | Technology |
|----------|------------|
| **Runtime** | Python 3.14+ |
| **Framework** | FastAPI 0.135+ |
| **Database** | PostgreSQL 15+ with asyncpg |
| **ORM** | SQLAlchemy 2.0 (AsyncIO) |
| **Migrations** | Alembic |
| **Auth** | JWT (python-jose), bcrypt |
| **Validation** | Pydantic v2 |
| **Server** | Uvicorn (ASGI) |
| **Package Manager** | uv |

---

## 📦 Installation

### Prerequisites

- Python 3.14 or higher
- PostgreSQL 15+ running locally or accessible via network
- [`uv`](https://github.com/astral-sh/uv) package manager (recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/utyara3/LeaderboardAPI.git
cd leaderboard-api-2
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_NAME=leaderboard_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Database Setup

```bash
# Create database (if not exists)
createdb leaderboard_db

# Run migrations (Alembic setup required)
alembic upgrade head
```

### 5. Run the Server

```bash
# Development mode with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📡 API Reference

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "player_one",
  "email": "player@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "player_one",
    "email": "player@example.com"
  }
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=player_one&password=securePassword123
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

---

### Leaderboard Endpoints

#### Create Leaderboard
```http
POST /leaderboards/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "slug": "speedrun-any-percent",
  "name": "Speedrun Any%",
  "fields_schema": {
    "time_ms": {"type": "integer"},
    "character": {"type": "string"},
    "version": {"type": "string"}
  },
  "sort_field": "time_ms",
  "sort_order": "asc"
}
```

**Supported Sort Orders:**
- `"asc"` — Lower values rank higher (e.g., time trials)
- `"desc"` — Higher values rank higher (e.g., scores)

#### Get Leaderboard by Slug
```http
GET /leaderboards/{slug}
```

#### Submit Entry
```http
POST /leaderboards/{slug}/submit
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "player_id": "player_123",
  "values": {
    "time_ms": 45320,
    "character": "Sonic",
    "version": "1.0"
  }
}
```

**Smart Update Logic:**
- If player has existing entry: only updates if new score is better
- Automatically recalculates ranks for all entries using window functions

#### Get Top Entries (Paginated)
```http
GET /leaderboards/{slug}/top?page=1&limit=10
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 10 | Entries per page (max: 100) |

#### Get Player's Best Entry
```http
GET /leaderboards/{slug}/player/{player_id}
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Leaderboards Table
```sql
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    owner_id UUID REFERENCES users(id) NOT NULL,
    fields_schema JSONB NOT NULL,
    sort_field VARCHAR NOT NULL,
    sort_order VARCHAR(4) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Entries Table
```sql
CREATE TABLE entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leaderboard_id UUID REFERENCES leaderboards(id) NOT NULL,
    player_id VARCHAR NOT NULL,
    values JSONB NOT NULL,
    rank INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for efficient ranking queries
CREATE INDEX idx_entries_leaderboard_rank
ON entries(leaderboard_id, rank ASC);
```

---

## 🔧 Development

### Project Structure

```
src/
├── api/                    # Route handlers
│   ├── auth.py            # Authentication endpoints
│   └── leaderboards.py    # Leaderboard endpoints
├── auth/                   # Authentication logic
│   ├── dependencies.py    # JWT dependency injection
│   └── utils.py           # Password hashing, token generation
├── models/                 # SQLAlchemy ORM models
│   ├── user.py
│   ├── leaderboard.py
│   └── entry.py
├── schemas/                # Pydantic validation schemas
│   ├── user.py
│   ├── leaderboard.py
│   ├── entry.py
│   └── query.py
├── services/               # Business logic layer
│   └── leaderboard_service.py
├── config.py              # Application configuration
├── database.py            # DB connection & session factory
└── main.py                # FastAPI application entry point
```

### Running Tests

```bash
# TODO: Add pytest configuration
pytest tests/ -v
```

### Code Quality

```bash
# TODO: Add linting and formatting
ruff check src/
black src/
```

---

## 🚧 Roadmap

This project is actively under development. Planned features include:

- [ ] **Batch Submissions** — Submit multiple entries in one request
- [ ] **Leaderboard Analytics** — Statistics, trends, and historical data
- [ ] **Webhooks** — Real-time notifications for rank changes
- [ ] **Admin Panel** — Moderation tools and leaderboard management UI
- [ ] **Rate Limiting** — API protection with configurable limits
- [ ] **Caching Layer** — Redis integration for frequently accessed leaderboards
- [ ] **Multi-tenant Support** — Isolated leaderboards per organization
- [ ] **GraphQL API** — Alternative query interface
- [ ] **Comprehensive Test Suite** — Unit, integration, and load tests
- [ ] **Docker Compose** — One-command local development setup
- [ ] **CI/CD Pipeline** — Automated testing and deployment

---

## 🔒 Security Considerations

- Passwords are hashed using **bcrypt** with automatic salt generation
- JWT tokens use **HS256** algorithm with configurable expiration
- All database queries use **parameterized statements** to prevent SQL injection
- Input validation enforced via **Pydantic v2** schemas
- CORS policies should be configured for production deployments

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
<p align="center">
  <em>Built with ❤️ using FastAPI</em>
</p>
