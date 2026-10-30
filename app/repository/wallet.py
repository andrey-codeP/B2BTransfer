from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from decimal import Decimal

from app.database.models import WalletTable


class WalletRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_wallet(self, user_id: int) -> WalletTable:
        """создаем кошелек по моделе SWalletCreate"""

        wallet = WalletTable(user_id=user_id)

        self.session.add(wallet)
        await self.session.flush()

        return wallet

    async def get_wallet_by_user_id(self, user_id: int) -> WalletTable | None:
        """получаем кошелек по айди юзера"""
        query = select(WalletTable).where(
            WalletTable.user_id == user_id,
            WalletTable.is_active == True,
        )
        result = await self.session.execute(query)
        wallet_model = result.scalar_one_or_none()

        if wallet_model is None:
            return None

        return wallet_model

    async def delete_wallet_by_id(self, wallet_id: int) -> bool:
        """мягко удаляем кошелек"""
        query = select(WalletTable).where(
            WalletTable.id == wallet_id, WalletTable.is_active == True
        )
        result = await self.session.execute(query)
        wallet_model = result.scalar_one_or_none()

        if wallet_model is None:
            return False

        wallet_model.is_active = False

        return True

    async def update_balance(
        self, wallet_id: int, amount: Decimal
    ) -> WalletTable | None:
        query = (
            select(WalletTable)
            .where(WalletTable.id == wallet_id, WalletTable.is_active == True)
            .with_for_update()
        )
        """обновляем кошелек пользователя
            с блокировкой транзакций"""
        wallet = await self.session.execute(query)
        wallet_model = wallet.scalar_one_or_none()

        if wallet_model is None:
            return None

        wallet_model.balance += amount

        return wallet_model
