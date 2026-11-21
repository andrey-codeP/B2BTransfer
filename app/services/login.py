from datetime import timedelta, datetime, timezone

from app.exceptions.token_exception import InvalidTokenError
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

        # проверку пароля и генерация токена вынесена вне uow что бы не держать
        # транзакцию открытой, потому что CPU задачи
        if password_manager.verify_password(password, hashed_password) is False:
            raise IncorrectPasswordError()

        access_token = TokenManager.create_access_token(user.id)
        refresh_token = TokenManager.create_refresh_token(user.id)
        expire_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        hashed_refresh_token = TokenManager.hash_token(refresh_token)

        async with self.uow as uow:
            await uow.token_rep.create_refresh_token(
                refresh_token=hashed_refresh_token,
                expire_at=expire_at,
                user_id=user.id,
            )

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh(self, refresh_token: str) -> dict:

        if not refresh_token:
            raise InvalidTokenError()

        user_id = TokenManager.decode_token(refresh_token, expected_type="refresh")
        hashed_token = TokenManager.hash_token(refresh_token)

        async with self.uow as uow:
            token_in_db = await uow.token_rep.get_refresh_token(hashed_token)

            if token_in_db.expires_at < datetime.now(timezone.utc):
                raise InvalidTokenError()

            new_access_token = TokenManager.create_access_token(user_id)
            new_refresh_token = TokenManager.create_refresh_token(user_id)

            new_expire_at = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            await uow.token_rep.expire_token_soon(hashed_token, seconds=10)
            await uow.token_rep.create_refresh_token(
                refresh_token=TokenManager.hash_token(new_refresh_token),
                expire_at=new_expire_at,
                user_id=user_id,
            )

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }

    async def logout(self, refresh_token: str | None) -> None:
        """Удаляем refresh токен из БД при выходе"""
        if not refresh_token:
            return

        hashed_token = TokenManager.hash_token(refresh_token)
        async with self.uow as uow:
            await uow.token_rep.delete_refresh_token(hashed_token)
