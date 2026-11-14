from fastapi import status
from httpx import AsyncClient
import pytest_asyncio
import pytest

from tests.conftest import RegisteredUser


@pytest_asyncio.fixture
async def created_wallet(test_client: AsyncClient, registered_user: RegisteredUser):
    """создаёт фикстуру которая создает кошелёк"""

    response = await test_client.post("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.mark.asyncio
async def test_create_wallet(test_client: AsyncClient, registered_user: RegisteredUser):
    """тестируем создание кошелька"""

    response = await test_client.post("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["balance"] == "0.00"


@pytest.mark.asyncio
async def test_create_wallet_duplicate(
    test_client: AsyncClient, registered_user: RegisteredUser, created_wallet
):
    """тестируем создание кошелька если уже есть"""

    response = await test_client.post("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["error_code"] == "wallet_already_exists"


@pytest.mark.asyncio
async def test_check_balance(
    test_client: AsyncClient, registered_user: RegisteredUser, created_wallet
):
    """тестируем првоерку баланса"""

    response = await test_client.get("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "0.00"


@pytest.mark.asyncio
async def test_check_balance_if_not_found(
    test_client: AsyncClient, registered_user: RegisteredUser
):
    """тестируем проверку баланса кошелька если кошелек не найден"""

    response = await test_client.get("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error_code"] == "wallet_not_found"


@pytest.mark.asyncio
async def test_delete_wallet(
    test_client: AsyncClient, registered_user: RegisteredUser, created_wallet
):
    """тестируем удаление кошелька, и убеждаемся то что API его не видет"""

    response = await test_client.delete("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get = await test_client.get("/wallet/", headers=registered_user.headers)

    assert get.status_code == status.HTTP_404_NOT_FOUND
    assert get.json()["error_code"] == "wallet_not_found"


@pytest.mark.asyncio
async def test_delete_wallet_if_not_found(
    test_client: AsyncClient, registered_user: RegisteredUser
):
    """тетсриуем удаление кошелька если его нет"""

    response = await test_client.delete("/wallet/", headers=registered_user.headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error_code"] == "wallet_not_found"
