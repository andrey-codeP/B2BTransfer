from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from decimal import Decimal
from typing import Sequence

from app.database.models.history import HistoryTransferTable


class HistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transfer_for_history(
        self, transfer_id: int, wallet_id: int, amount_change: Decimal
    ) -> HistoryTransferTable:
        """создаем историю трансферов"""
        hist_model = HistoryTransferTable(
            transfer_id=transfer_id, wallet_id=wallet_id, amount_change=amount_change
        )
        self.session.add(hist_model)

        return hist_model

    async def get_history_by_wallet_id(
            self,
            wallet_id: int,
            limit: int = 20,
            offset: int = 0,
    ) -> Sequence[HistoryTransferTable]:
        """получаем историю трансферов с пагинацией"""
        query = (
            select(HistoryTransferTable)
            .where(HistoryTransferTable.wallet_id == wallet_id)
            .order_by(HistoryTransferTable.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
