from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DECIMAL, func, DateTime

from decimal import Decimal
from datetime import datetime

from app.database.models.base import Base


class HistoryTransferTable(Base):
    __tablename__ = "history_transfers"

    id: Mapped[int] = mapped_column(primary_key=True)

    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id"))
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), index=True)

    amount_change: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    transfer: Mapped["TransferTable"] = relationship(back_populates="history_entries")
    wallet: Mapped["WalletTable"] = relationship(back_populates="history_entries")
