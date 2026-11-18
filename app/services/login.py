from datetime import timedelta, datetime, timezone


from app.exceptions.user_exception import IncorrectPasswordError, UserNotFoundError
from app.database.uow import UnitOfWork
from app.security.login import TokenManager
from app.security import password_manager
from app.config import settings


class LoginService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def login(self, username: str, password: str) -> dict:
        """выдаем юзеру аксес и рефреш токен после проверок"""
        async with self.uow as uow:
            user = await uow.user_rep.get_user_by_username(username=username)

        if user is None:
            raise UserNotFoundError()

        hashed_password = user.hashed_password

        if password_manager.verify_password(password, hashed_password) is False:
            raise IncorrectPasswordError()

        access_token = TokenManager.create_access_token(user.id)
        refresh_token = TokenManager.create_refresh_token(user.id)
        expire_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        async with self.uow as uow:
            await uow.token_rep.create_refresh_token(
                refresh_token=refresh_token,
                expire_at=expire_at,
                user_id=user.id,
            )

        return {"access_token": access_token, "refresh_token": refresh_token}
