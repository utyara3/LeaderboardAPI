# 🏆 Leaderboard API

> **High-performance async leaderboard service** built with FastAPI, PostgreSQL and Docker.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

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

*   **API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
*   **Database:** Available at `localhost:5433` (User/Pass defined in `.env`)

To stop the services:
```bash
docker compose down
```

---

## ✨ Features

*   🔐 **Secure Authentication:** JWT-based auth with registration and login endpoints.
*   ⚡ **Async Architecture:** Built on FastAPI and SQLAlchemy 2.0 (async) for high concurrency.
*   📊 **Dynamic Leaderboards:** Flexible JSONB schema allows custom fields for different game types (e.g., time trials vs. high scores).
*   🔄 **Smart Updates:** Optimistic locking ensures entries are only updated if the new score is better.
*   🐳 **Production-Ready Docker:** Fully containerized setup with automatic migrations via Alembic.

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Framework** | FastAPI |
| **Database** | PostgreSQL 15 + asyncpg |
| **ORM** | SQLAlchemy 2.0 (AsyncIO) |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Package Manager** | uv |
| **Containerization** | Docker & Docker Compose |

---

## 📂 Project Structure

```text
.
├── alembic/                # Database migrations
├── src/
│   ├── api/                # Route handlers (Auth, Leaderboards)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic validation schemas
│   ├── services/           # Business logic layer
│   ├── config.py           # App configuration
│   ├── database.py         # DB connection factory
│   └── main.py             # Application entry point
├── docker-compose.yml      # Orchestration config
├── Dockerfile              # Image build instructions
├── .env.example            # Environment template
└── README.md
```

---

## 🧪 Local Development (Without Docker)

If you prefer running locally:

1.  **Install dependencies:**
    ```bash
    uv sync
    ```
2.  **Set up Database:**
    Ensure PostgreSQL is running and create a database. Update `.env` with your local credentials.
3.  **Run Migrations:**
    ```bash
    alembic upgrade head
    ```
4.  **Start Server:**
    ```bash
    uvicorn src.main:app --reload
    ```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <em>Built with ❤️ by utyara3</em>
</p>

