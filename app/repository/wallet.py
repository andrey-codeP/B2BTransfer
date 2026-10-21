from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.wallet import SWalletResponse, SWalletCreate
from app.database.models import WalletTable


class WalletRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_wallet(self, wallet_data: SWalletCreate) -> SWalletResponse:
        """создаем кошелек по моделе SWalletCreate"""
        wallet_model = wallet_data.model_dump()

        wallet = WalletTable(**wallet_model)

        self.session.add(wallet)
        await self.session.commit()
        await self.session.refresh(wallet)

        return SWalletResponse.model_validate(wallet)

    async def get_wallet_by_user_id(self, user_id: int) -> SWalletResponse | None:
        """получаем кошелек по айди юзера"""
        query = select(WalletTable).where(
            WalletTable.user_id == user_id,
            WalletTable.is_active == True,
        )
        result = await self.session.execute(query)
        wallet_model = result.scalar_one_or_none()

        if wallet_model is None:
            return None

        return SWalletResponse.model_validate(wallet_model)

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
        await self.session.commit()

        return True
