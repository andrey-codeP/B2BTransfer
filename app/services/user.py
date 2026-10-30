from app.exceptions.user_exception import UsernameAlreadyExistsError, UserNotFoundError
from app.schemas.user import SUserCreate, SUserResponse
from app.database.models import UserTable
from app.security import password_manager
from app.database.uow import UnitOfWork


class UserServices:
    """сервис для работы с юзером"""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_user(self, user_data: SUserCreate) -> SUserResponse:
        """создаем пользователя"""
        hashed_password = password_manager.create_hash_password(user_data.password)

        async with self.uow as uow:
            existing = await uow.user_rep.get_user_by_username(user_data.username)

            if existing is not None:
                raise UsernameAlreadyExistsError()

            user = UserTable(
                username=user_data.username,
                hashed_password=hashed_password,
            )

            created_user = await uow.user_rep.create_user(user)

        return SUserResponse.model_validate(created_user)

    async def get_user_by_id(self, user_id: int) -> SUserResponse:
        """получаем пользователя по айди"""
        async with self.uow as uow:
            user = await uow.user_rep.get_user_by_id(user_id)

            if user is None:
                raise UserNotFoundError()

        return SUserResponse.model_validate(user)

    async def get_user_by_username(self, username: str) -> SUserResponse:
        """получаем пользователя по юзернейму"""
        async with self.uow as uow:
            user = await uow.user_rep.get_user_by_username(username)

            if user is None:
                raise UserNotFoundError()

        return SUserResponse.model_validate(user)

    async def delete_user_by_id(self, user_id: int) -> bool:
        """удаляем пользователя по айди"""
        async with self.uow as uow:
            existing = await uow.user_rep.delete_by_id(user_id)

            if existing is False:
                raise UserNotFoundError()

        return True

    async def update_username(self, user_id: int, new_username: str) -> SUserResponse:
        """обновляем пользователя, с проверкой
        не занят ли новый юзернейм"""
        async with self.uow as uow:
            existing_with_new_username = await uow.user_rep.get_user_by_username(
                new_username
            )

            if existing_with_new_username is not None:
                raise UsernameAlreadyExistsError()

            existing = await uow.user_rep.change_username(user_id, new_username)

            if existing is None:
                raise UserNotFoundError()

        return SUserResponse.model_validate(existing)
