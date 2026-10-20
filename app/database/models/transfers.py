from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric, DateTime, func

from datetime import datetime

from app.database.models.base import Base


class TransferTable(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(primary_key=True)

    to_wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id", ondelete="RESTRICT")
    )
    from_wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id", ondelete="RESTRICT")
    )

    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    from_wallet: Mapped["WalletTable"] = relationship(
        "WalletTable", foreign_keys=[from_wallet_id]
    )
    to_wallet: Mapped["WalletTable"] = relationship(
        "WalletTable", foreign_keys=[to_wallet_id]
    )

    history_entries: Mapped[list["HistoryTransferTable"]] = relationship(
        back_populates="transfer"
    )
