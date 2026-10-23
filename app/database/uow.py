from sqlalchemy.ext.asyncio import AsyncSession

from types import TracebackType

from app.repository.user import UserRepository
from app.repository.wallet import WalletRepository
from app.repository.transfers import TransferRepository
from app.repository.history import HistoryRepository


class UnitOfWork:
    """manages a database transaction and provides repositories sharing one session."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

        self.user_rep = UserRepository(session)
        self.wallet_rep = WalletRepository(session)
        self.transfer_rep = TransferRepository(session)
        self.history_rep = HistoryRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(
            self, exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> None:
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()

