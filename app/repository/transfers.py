from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.transfers import STransferCreate
from app.database.models import TransferTable


class TransferRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transfer(self, transfer: STransferCreate) -> TransferTable | None:
        """создаем транзакцию в бд"""
        transfer_data = transfer.model_dump()
        transfer_table = TransferTable(**transfer_data)

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
