# tests/conftest.py

from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool  # ← ДОБАВЬ ЭТО

from src.main import app
from src.core.database import get_db, Base
from src.core.config import settings

# Отключаем middleware для тестов
app.user_middleware.clear()

# URL тестовой БД
TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_pass@localhost:5434/test_leaderboard_db"
)

# ← КЛЮЧЕВОЕ: NullPool отключает пулинг соединений
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # ← Каждое соединение создаётся заново
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Создаёт НОВУЮ сессию для каждого запроса"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Создаёт таблицы перед тестами, удаляет после"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture
async def client():
    """HTTP клиент для тестов"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """Фикстура с токеном авторизации"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
    }
    await client.post("/auth/register", json=user_data)

    login_data = {"username": "testuser", "password": "Password123!"}
    response = await client.post("/auth/login", data=login_data)
    tokens = response.json()

    return {"Authorization": f"Bearer {tokens['access_token']}"}
