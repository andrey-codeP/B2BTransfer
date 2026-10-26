from decimal import Decimal

from app.exceptions.transfer_exception import InsufficientFundsError
from app.exceptions.wallet_exception import WalletNotFoundError
from app.database.uow import UnitOfWork


class TransferService:
    """сервис для управления переводов между пользователей"""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_transfer(
        self, sender_user_id: int, recipient_user_id: int, amount: Decimal
    ) -> bool:
        """овтечает за безопасные переводы между пользователями"""
        async with self.uow as uow:
            sender = await uow.wallet_rep.get_wallet_by_user_id(sender_user_id)
            recipient = await uow.wallet_rep.get_wallet_by_user_id(recipient_user_id)

            if not sender or not recipient:
                raise WalletNotFoundError()

            first_id, second_id = sorted([sender.id, recipient.id])

            await uow.wallet_rep.update_balance(first_id, Decimal("0.00"))
            await uow.wallet_rep.update_balance(second_id, Decimal("0.00"))

            await uow.session.refresh(sender)
            await uow.session.refresh(recipient)

            if sender.balance < amount:
                raise InsufficientFundsError()

            await uow.wallet_rep.update_balance(sender.id, -amount)
            await uow.wallet_rep.update_balance(recipient.id, amount)

            transfer = await uow.transfer_rep.create_transfer(
                amount, sender.id, recipient.id
            )
            await uow.history_rep.create_transfer_for_history(
                transfer_id=transfer.id, wallet_id=sender.id, amount_change=-amount
            )
            await uow.history_rep.create_transfer_for_history(
                transfer_id=transfer.id, wallet_id=recipient.id, amount_change=amount
            )
        return True

