from fastapi import status
from httpx import AsyncClient
import pytest

from decimal import Decimal

from app.security.login import TokenManager
from app.main import app


@pytest.mark.asyncio
async def test_create_wallet(test_client: AsyncClient, user_model: dict):
    create_user = await test_client.post("/auth/registry", json=user_model)
    assert create_user.status_code == status.HTTP_201_CREATED

    user_id = create_user.json()["id"]
    app.dependency_overrides[TokenManager.get_id_by_access_token] = lambda: user_id

    result = await test_client.post("/wallet/", json={"user_id": user_id})
    assert result.status_code == status.HTTP_201_CREATED
    assert result.json().get("user_id") == user_id
    assert Decimal(result.json().get("balance")) == Decimal("0.00")
