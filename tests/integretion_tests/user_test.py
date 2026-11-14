from httpx import AsyncClient
from fastapi import status
import pytest


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
