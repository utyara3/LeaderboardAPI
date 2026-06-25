async def test_login_wrong_password(client: AsyncClient):
    """Логин с неверным паролем"""
    await client.post(
        "/auth/register",
        json={
            "username": "wrongpass",
            "email": "wrong@example.com",
            "password": "Password123!",
        },
    )

    response = await client.post(
        "/auth/login", data={"username": "wrongpass", "password": "WrongPassword123!"}
    )
    # ← ИЗМЕНЕНО: 400 вместо 401 (API не раскрывает что пользователь существует)
    assert response.status_code == 400


async def test_refresh_token(client: AsyncClient):
    """Обновление токена"""
    # Регистрируем и логинимся
    await client.post(
        "/auth/register",
        json={
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "Password123!",
        },
    )
    login = await client.post(
        "/auth/login", data={"username": "refreshuser", "password": "Password123!"}
    )
    refresh_token = login.json()["refresh_token"]

    # ← ИЗМЕНЕНО: Передаём refresh_token как query parameter
    response = await client.post(f"/auth/refresh?refresh_token={refresh_token}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Новый refresh должен отличаться от старого
    assert data["refresh_token"] != refresh_token


async def test_logout(client: AsyncClient):
    """Logout отзывает refresh токен"""
    # Регистрируем и логинимся
    await client.post(
        "/auth/register",
        json={
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": "Password123!",
        },
    )
    login = await client.post(
        "/auth/login", data={"username": "logoutuser", "password": "Password123!"}
    )
    refresh_token = login.json()["refresh_token"]

    # ← ИЗМЕНЕНО: Передаём refresh_token как query parameter
    response = await client.post(f"/auth/logout?refresh_token={refresh_token}")
    assert response.status_code == 200

    # Пытаемся refresh после logout — должно вернуть 401
    response = await client.post(f"/auth/refresh?refresh_token={refresh_token}")
    assert response.status_code == 401
