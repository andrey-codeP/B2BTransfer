from httpx import AsyncClient
from fastapi import status
import pytest_asyncio
import pytest

from dataclasses import dataclass
from decimal import Decimal
import asyncio

from app.repository.history import HistoryRepository
from app.repository.wallet import WalletRepository
from tests.conftest import RegisteredUser


@dataclass
class TransferActors:
    """модель для отправителя и получателя"""

    sender_id: int
    sender_headers: dict
    recipient_id: int
    recipient_headers: dict


@pytest_asyncio.fixture
async def funded_transfer_actors(
    test_client: AsyncClient, registered_user: RegisteredUser, session_factory
):
    """
    создаёт отправителя с балансом 100 и получателя с балансом 0
    """
    # создаем владельцев и их кашельки
    recipient_data = {
        "username": "recipient_user",
        "password": "password123",
    }  # данные получателя
    reg = await test_client.post("/auth/registry", json=recipient_data)
    assert reg.status_code == status.HTTP_201_CREATED
    recipient_id = reg.json()["id"]

    login = await test_client.post(
        "/auth/login",
        data={
            "username": recipient_data["username"],
            "password": recipient_data["password"],
        },
    )
    recipient_token = login.json()["access_token"]
    recipient_headers = {"Authorization": f"Bearer {recipient_token}"}
    await test_client.post(
        "/wallet/", headers=recipient_headers
    )  # создает кошелек получателю
    await test_client.post(
        "/wallet/", headers=registered_user.headers
    )  # создает кошелек отправителю

    # начисляем балансы через репозиторий
    async with session_factory() as session:
        repo = WalletRepository(session)

        # отправителю — 100
        sender_wallet = await repo.get_wallet_by_user_id(registered_user.id)
        sender_wallet.balance = Decimal("100.00")

        # получателю — 10
        recipient_wallet = await repo.get_wallet_by_user_id(recipient_id)
        recipient_wallet.balance = Decimal("10.00")

        await session.commit()

    return TransferActors(
        sender_id=registered_user.id,
        sender_headers=registered_user.headers,
        recipient_id=recipient_id,
        recipient_headers=recipient_headers,
    )


@pytest.mark.asyncio
async def test_transfer_with_two_user(
    test_client: AsyncClient,
    session_factory,
    funded_transfer_actors: TransferActors,
    monkeypatch,
):
    """тестируем паралельный перевод с кошелька A на кошелек B и с B на A"""

    actors_model = funded_transfer_actors

    original_lock = WalletRepository.get_wallet_by_id_for_update
    lock_calls = 0

    async def slow_lock(self, wallet_id):
        """замедляем первый запрос для того что бы проверить FOR UPDATE
        остальные запросы не будут замедленны"""

        nonlocal lock_calls
        lock_calls += 1
        if lock_calls == 1:  # проверка надо ли замедлять запрос
            await asyncio.sleep(0.5)
        return await original_lock(self, wallet_id)

    # применяем замедленее
    monkeypatch.setattr(WalletRepository, "get_wallet_by_id_for_update", slow_lock)

    transfer_1 = test_client.post(
        "/transfers/transfer",
        headers=actors_model.sender_headers,
        json={"recipient_user_id": actors_model.recipient_id, "amount": "10.00"},
    )
    transfer_2 = test_client.post(
        "/transfers/transfer",
        headers=actors_model.recipient_headers,  # нужен хедер получателя
        json={"recipient_user_id": actors_model.sender_id, "amount": "10.00"},
    )

    result = await asyncio.gather(transfer_1, transfer_2)

    for res in result:
        assert res.status_code == status.HTTP_201_CREATED

    async with session_factory() as session:
        wallet_rep = WalletRepository(session)
        sender_wallet = await wallet_rep.get_wallet_by_user_id(actors_model.sender_id)
        recipient_wallet = await wallet_rep.get_wallet_by_user_id(
            actors_model.recipient_id
        )

        # првоеряем правильно ли начислились деньги
        assert sender_wallet.balance == Decimal("100.00")
        assert recipient_wallet.balance == Decimal("10.00")

        history_rep = HistoryRepository(session)

        sender_history = await history_rep.get_history_by_wallet_id(sender_wallet.id)
        recipient_history = await history_rep.get_history_by_wallet_id(
            recipient_wallet.id
        )
        # проверяем правильное ли количество записей
        assert len(sender_history) == len(recipient_history) == 2

        # проверяем суммы (что списали и зачислили именно 10)
        sender_amounts = sorted([h.amount_change for h in sender_history])
        recipient_amounts = sorted([h.amount_change for h in recipient_history])

        assert sender_amounts == [Decimal("-10.00"), Decimal("10.00")]
        assert recipient_amounts == [Decimal("-10.00"), Decimal("10.00")]
