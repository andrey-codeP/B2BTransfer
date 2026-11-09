from fastapi import status
import pytest

from app.security import password_manager
from app.database.models import UserTable


@pytest.mark.asyncio
async def test_registry_user(test_client, user_model):
    result = await test_client.post("/auth/registry", json=user_model)
    result_data = result.json()

    assert result.status_code == status.HTTP_201_CREATED
    assert result_data.get("username") == user_model.get("username")


@pytest.mark.asyncio
async def test_login_user(test_client, user_model):
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
