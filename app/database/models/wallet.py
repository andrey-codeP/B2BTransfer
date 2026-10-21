from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DECIMAL, ForeignKey

from decimal import Decimal

from app.database.models.base import Base


class WalletTable(Base):
    """кошелек для юзера"""

    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)

    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2), server_default="0.00", nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    user: Mapped["UserTable"] = relationship(back_populates="wallet")

    sent_transfer: Mapped[list["TransferTable"]] = relationship(
        "TransferTable",
        primaryjoin="WalletTable.id == TransferTable.from_wallet_id",
        back_populates="from_wallet",
    )

    recieve_transfer: Mapped[list["TransferTable"]] = relationship(
        "TransferTable",
        primaryjoin="WalletTable.id == TransferTable.to_wallet_id",
        back_populates="to_wallet",
    )

    history_entries: Mapped[list["HistoryTransferTable"]] = relationship(
        back_populates="wallet"
    )
