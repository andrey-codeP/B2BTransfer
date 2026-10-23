from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from decimal import Decimal

from app.database.models import TransferTable


class TransferRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_transfer(
        self, amount: Decimal, from_wallet_id: int, to_wallet_id: int
    ) -> TransferTable:
        """создаем транзакцию в бд"""
        transfer_table = TransferTable(
            amount=amount,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
        )

        self.session.add(transfer_table)

        return transfer_table

    async def get_transfer(self, transfer_id: int) -> TransferTable | None:
        """получаем нужную транзакцию по айди"""
        query = select(TransferTable).where(TransferTable.id == transfer_id)
        result = await self.session.execute(query)

        transfer_model = result.scalar_one_or_none()

        if transfer_model is None:
            return None

        return transfer_model
