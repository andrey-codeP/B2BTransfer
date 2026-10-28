from app.exceptions.user_exception import IncorrectPasswordError, UserNotFoundError
from app.database.uow import UnitOfWork
from app.security.login import TokenManager
from app.security import password_manager


class LoginService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def login(self, username, password):
        async with self.uow as uow:
            user = await uow.user_rep.get_user_by_username(username=username)

        if user is None:
            raise UserNotFoundError()

        user_id, hashed_password = user.id, user.hashed_password

        if password_manager.verify_password(password, hashed_password) is False:
            raise IncorrectPasswordError()

        token: str = TokenManager.create_access_token(user_id=user_id)

        return token
