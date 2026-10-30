from decimal import Decimal

from app.exceptions.transfer_exception import InsufficientFundsError, SelfTransferError
from app.exceptions.wallet_exception import WalletNotFoundError, WalletAccessDeniedError
from app.database.uow import UnitOfWork


class TransferService:
    """сервис для управления переводов между пользователей"""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_transfer(
        self, sender_user_id: int, recipient_user_id: int, amount: Decimal
    ) -> bool:
        """овтечает за безопасные переводы между пользователями"""
        if sender_user_id == recipient_user_id:
            raise SelfTransferError()

        async with self.uow as uow:
            sender_init = await uow.wallet_rep.get_wallet_by_user_id(sender_user_id)
            recipient_init = await uow.wallet_rep.get_wallet_by_user_id(
                recipient_user_id
            )

            if not sender_init or not recipient_init:
                raise WalletNotFoundError()

            first_id, second_id = sorted([sender_init.id, recipient_init.id])

            wallet1 = await uow.wallet_rep.get_wallet_by_id_for_update(first_id)
            wallet2 = await uow.wallet_rep.get_wallet_by_id_for_update(second_id)

            if not wallet1 or not wallet2:
                raise WalletNotFoundError()

            sender = wallet1 if sender_init.id == first_id else wallet2
            recipient = wallet2 if sender_init.id == first_id else wallet1


            if sender.balance < amount:
                raise InsufficientFundsError()

            sender.balance -= amount
            recipient.balance += amount

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
