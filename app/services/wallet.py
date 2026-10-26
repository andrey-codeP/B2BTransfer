from app.exceptions.wallet_exception import (
    WalletAlreadyExistsError,
    WalletNotFoundError,
)
from app.schemas.wallet import SWalletResponse
from app.database.uow import UnitOfWork


class WalletService:
    """сервис для работы с кошельком"""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_wallet_by_user_id(self, user_id: int) -> SWalletResponse:
        """создаёт кошелёк для пользователя"""
        async with self.uow as uow:
            existing = await uow.wallet_rep.get_wallet_by_user_id(user_id)

            if existing is not None:
                raise WalletAlreadyExistsError()

            wallet_model = await uow.wallet_rep.create_wallet(user_id)

        return SWalletResponse.model_validate(wallet_model)

    async def get_wallet_user_id(self, user_id: int) -> SWalletResponse:
        """получаем кошелек по айди его владельца"""
        async with self.uow as uow:
            wallet_model = await uow.wallet_rep.get_wallet_by_user_id(user_id)

            if wallet_model is None:
                raise WalletNotFoundError()

        return SWalletResponse.model_validate(wallet_model)

    async def delete_wallet(self, wallet_id: int) -> bool:
        """удаляет кошелек"""
        async with self.uow as uow:
            wallet_model = await uow.wallet_rep.delete_wallet_by_id(wallet_id)

            if wallet_model is False:
                raise WalletNotFoundError()

        return True
