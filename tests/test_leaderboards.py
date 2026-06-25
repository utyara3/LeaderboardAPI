import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_leaderboard(client: AsyncClient, auth_headers: dict):
    """Создание лидерборда"""
    response = await client.post(
        "/leaderboards/",
        json={
            "slug": "test-board",
            "name": "Test Leaderboard",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "test-board"
    assert data["name"] == "Test Leaderboard"


async def test_create_leaderboard_duplicate_slug(
    client: AsyncClient, auth_headers: dict
):
    """Создание лидерборда с дублирующимся slug"""
    # Создаём первый
    await client.post(
        "/leaderboards/",
        json={
            "slug": "duplicate",
            "name": "First",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )

    # Пытаемся создать второй с тем же slug
    response = await client.post(
        "/leaderboards/",
        json={
            "slug": "duplicate",
            "name": "Second",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_get_all_leaderboards(client: AsyncClient, auth_headers: dict):
    """Получение списка лидербордов"""
    # Создаём несколько
    for i in range(3):
        await client.post(
            "/leaderboards/",
            json={
                "slug": f"board-{i}",
                "name": f"Board {i}",
                "fields_schema": {"score": {"type": "integer"}},
                "sort_field": "score",
                "sort_order": "desc",
            },
            headers=auth_headers,
        )

    response = await client.get("/leaderboards/?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


async def test_submit_entry(client: AsyncClient, auth_headers: dict):
    """Отправка результата"""
    # Создаём лидерборд
    await client.post(
        "/leaderboards/",
        json={
            "slug": "submit-test",
            "name": "Submit Test",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )

    # Отправляем результат
    response = await client.post(
        "/leaderboards/submit-test/submit",
        json={"player_id": "player1", "values": {"score": 100}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "player1"
    assert data["values"]["score"] == 100


async def test_get_top_entries(client: AsyncClient, auth_headers: dict):
    """Получение топа"""
    # Создаём лидерборд
    await client.post(
        "/leaderboards/",
        json={
            "slug": "top-test",
            "name": "Top Test",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )

    # Отправляем несколько результатов
    for i, score in enumerate([100, 200, 150]):
        await client.post(
            "/leaderboards/top-test/submit",
            json={"player_id": f"player{i}", "values": {"score": score}},
            headers=auth_headers,
        )

    # Получаем топ
    response = await client.get("/leaderboards/top-test/top?limit=10&page=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Проверяем порядок (desc: 200, 150, 100)
    assert data[0]["values"]["score"] == 200
    assert data[1]["values"]["score"] == 150
    assert data[2]["values"]["score"] == 100


async def test_update_leaderboard_owner(client: AsyncClient, auth_headers: dict):
    """Обновление лидерборда владельцем"""
    # Создаём
    await client.post(
        "/leaderboards/",
        json={
            "slug": "update-test",
            "name": "Old Name",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )

    # Обновляем — передаём все поля которые могут быть в схеме
    response = await client.put(
        "/leaderboards/update-test",
        json={
            "name": "New Name",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


async def test_update_leaderboard_not_owner(client: AsyncClient, auth_headers: dict):
    """Обновление лидерборда не владельцем — 403"""
    # Создаём лидерборд от первого пользователя
    await client.post(
        "/leaderboards/",
        json={
            "slug": "forbidden-test",
            "name": "Forbidden",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )

    # Регистрируем второго пользователя
    await client.post(
        "/auth/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "Password123!",
        },
    )
    login = await client.post(
        "/auth/login", data={"username": "otheruser", "password": "Password123!"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Пытаемся обновить от имени второго пользователя
    response = await client.put(
        "/leaderboards/forbidden-test",
        json={
            "name": "Hacked",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_delete_leaderboard(client: AsyncClient, auth_headers: dict):
    """Удаление лидерборда"""
    # Создаём
    await client.post(
        "/leaderboards/",
        json={
            "slug": "delete-test",
            "name": "Delete Me",
            "fields_schema": {"score": {"type": "integer"}},
            "sort_field": "score",
            "sort_order": "desc",
        },
        headers=auth_headers,
    )

    # Удаляем
    response = await client.delete("/leaderboards/delete-test", headers=auth_headers)
    assert response.status_code == 200

    # Проверяем что удалён
    response = await client.get("/leaderboards/delete-test")
    assert response.status_code == 404
