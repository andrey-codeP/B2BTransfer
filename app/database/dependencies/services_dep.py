from fastapi import Depends

from typing import Annotated

from app.database.dependencies.depends import UOWDep
from app.services.user import UserServices
from app.services.login import LoginService
from app.services.wallet import WalletService
from app.services.transfers import TransferService


def get_user_service(uow: UOWDep) -> UserServices:
    """зависемость возращающая сервис для работы с юзерами"""
    return UserServices(uow)


UserServiceDep = Annotated[UserServices, Depends(get_user_service)]


def get_login_service(uow: UOWDep) -> LoginService:
    """зависемость выдающая сервис для работы с логинами"""
    return LoginService(uow)


LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]


def get_wallet_service(uow: UOWDep) -> WalletService:
    """зависемость выдающая сервис для работы с кошельком"""
    return WalletService(uow)


WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]


def get_transfers_service(uow: UOWDep) -> TransferService:
    """зависемость выдающая зависемость для работы с трансферами"""
    return TransferService(uow)


TransferServiceDep = Annotated[TransferService, Depends(get_transfers_service)]
