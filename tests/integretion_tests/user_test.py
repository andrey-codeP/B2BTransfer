from httpx import AsyncClient
from fastapi import status
import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import update

from app.database.models import RefreshToken
from app.security.login import TokenManager


@pytest.mark.asyncio
async def test_refresh_token_success(test_client: AsyncClient, user_model: dict):
    """успешное обновление токенов и ротация refresh_token в куках"""
    await test_client.post("/auth/registry", json=user_model)
    login_res = await test_client.post("/auth/login", data=user_model)
    assert login_res.status_code == status.HTTP_200_OK

    old_access = login_res.json()["access_token"]
    old_refresh = test_client.cookies.get("refresh_token")
    assert old_refresh is not None

    # httpx сам подставит куку refresh_token из своего cookie jar
    refresh_res = await test_client.post("/auth/refresh")
    assert refresh_res.status_code == status.HTTP_200_OK

    new_access = refresh_res.json()["access_token"]
    new_refresh = test_client.cookies.get("refresh_token")

    assert new_access is not None
    assert new_access != old_access
    assert new_refresh is not None
    assert new_refresh != old_refresh


@pytest.mark.asyncio
async def test_refresh_token_missing(test_client: AsyncClient):
    """Ошибка 401, если кука refresh_token не передана"""
    res = await test_client.post("/auth/refresh")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token_invalid_string(test_client: AsyncClient):
    """ошибка 401 и очистка куки при передаче невалидного токена"""
    res = await test_client.post(
        "/auth/refresh",
        headers={"Cookie": "refresh_token=invalid.jwt.token"},
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    set_cookie = res.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "Max-Age=0" in set_cookie


@pytest.mark.asyncio
async def test_refresh_token_access_instead_of_refresh(
    test_client: AsyncClient, user_model: dict
):
    """ошибка 401, если в куку подсунули access_token вместо refresh_token"""
    await test_client.post("/auth/registry", json=user_model)
    login_res = await test_client.post("/auth/login", data=user_model)
    access_token = login_res.json()["access_token"]

    test_client.cookies.set("refresh_token", access_token)

    res = await test_client.post("/auth/refresh")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token_expired_in_db(
    test_client: AsyncClient, user_model: dict, session_factory
):
    """ошибка 401, если срок жизни токена в БД истек"""
    await test_client.post("/auth/registry", json=user_model)
    await test_client.post("/auth/login", data=user_model)
    refresh_token = test_client.cookies.get("refresh_token")
    hashed = TokenManager.hash_token(refresh_token)

    # принудительно делаем токен протухшим в БД
    async with session_factory() as session:
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.refresh_token == hashed)
            .values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        )
        await session.commit()

    res = await test_client.post("/auth/refresh")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token_race_condition_grace_period(
    test_client: AsyncClient, user_model: dict
):
    """параллельные запросы с одним refresh_token проходят успешно благодаря grace period"""
    await test_client.post("/auth/registry", json=user_model)
    await test_client.post("/auth/login", data=user_model)
    refresh_token = test_client.cookies.get("refresh_token")

    # Имитируем 3 одновременных запроса с одним и тем же старым токеном
    responses = await asyncio.gather(
        test_client.post(
            "/auth/refresh", headers={"Cookie": f"refresh_token={refresh_token}"}
        ),
        test_client.post(
            "/auth/refresh", headers={"Cookie": f"refresh_token={refresh_token}"}
        ),
        test_client.post(
            "/auth/refresh", headers={"Cookie": f"refresh_token={refresh_token}"}
        ),
    )

    for res in responses:
        assert res.status_code == status.HTTP_200_OK
        assert res.json().get("access_token") is not None


@pytest.mark.asyncio
async def test_logout_invalidates_refresh_token(
    test_client: AsyncClient, user_model: dict
):
    """после /logout кука удаляется, а старый refresh_token больше не работает"""
    await test_client.post("/auth/registry", json=user_model)
    await test_client.post("/auth/login", data=user_model)
    saved_refresh = test_client.cookies.get("refresh_token")

    logout_res = await test_client.post("/auth/logout")
    assert logout_res.status_code == status.HTTP_204_NO_CONTENT
    assert not test_client.cookies.get("refresh_token")

    # передаем куку через заголовок, чтобы не вызывать DeprecationWarning в httpx
    refresh_res = await test_client.post(
        "/auth/refresh",
        headers={"Cookie": f"refresh_token={saved_refresh}"},
    )
    assert refresh_res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_registry_user(test_client: AsyncClient, user_model: dict):
    """проверяем базовый счастливый сценарий при создании пользователя"""

    result = await test_client.post("/auth/registry", json=user_model)
    result_data = result.json()

    assert result.status_code == status.HTTP_201_CREATED
    assert result_data["username"] == user_model["username"]


@pytest.mark.asyncio
async def test_registry_user_if_he_exists(test_client: AsyncClient, user_model: dict):
    """тестируем бед случай если пользователь с таким юзером уже есть"""

    result = await test_client.post("/auth/registry", json=user_model)
    assert result.status_code == status.HTTP_201_CREATED

    repeated_result = await test_client.post("/auth/registry", json=user_model)
    assert repeated_result.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_login_user(test_client: AsyncClient, user_model: dict):
    """тестируем регистрации и логина"""

    reg = await test_client.post("/auth/registry", json=user_model)
    assert reg.status_code == status.HTTP_201_CREATED

    login_payload = {
        "username": user_model.get("username"),
        "password": user_model.get("password"),
    }

    login_result = await test_client.post("/auth/login", data=login_payload)
    assert login_result.status_code == status.HTTP_200_OK

    login_data = login_result.json()
    assert login_data.get("access_token") is not None
    assert login_data.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_user_if_not_exist(test_client: AsyncClient):
    """тестируем логин если пользователя нет в бд"""

    fake_payload = {
        "username": "non_existent_user",
        "password": "ValidPassword123",
    }
    login_result = await test_client.post("/auth/login", data=fake_payload)
    assert login_result.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_login_if_password_no_correct(test_client: AsyncClient, user_model: dict):
    """тестируем логин если пользователь с юзернеймом есть но пароль не верен"""

    reg = await test_client.post("/auth/registry", json=user_model)

    fake_payload = {
        "username": user_model.get("username"),
        "password": "011100 111000 11000119358123907859",
    }

    login_result = await test_client.post("/auth/login", data=fake_payload)
    assert login_result.status_code == status.HTTP_401_UNAUTHORIZED
