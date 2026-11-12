from fastapi import status
from httpx import AsyncClient
import pytest

from decimal import Decimal

from app.security.login import TokenManager
from app.main import app


@pytest.mark.asyncio
async def test_create_wallet(registered_user, test_client: AsyncClient, user_model: dict):
    result = await test_client.post("/wallet/", headers=registered_user.headers)
    assert result.status_code == status.HTTP_201_CREATED
    assert result.json().get("user_id") == registered_user.id
    assert Decimal(result.json().get("balance")) == Decimal("0.00")
