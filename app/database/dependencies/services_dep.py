from fastapi import Depends

from typing import Annotated

from app.database.dependencies.depends import UOWDep
from app.services.user import UserServices
from app.services.login import LoginService


def get_user_service(uow: UOWDep) -> UserServices:
    return UserServices(uow)


UserServiceDep = Annotated[UserServices, Depends(get_user_service)]


def get_login_service(uow: UOWDep) -> LoginService:
    return LoginService(uow)


LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]
