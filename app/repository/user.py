from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.security import password_manager
from app.database.models import UserTable


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user: UserTable) -> UserTable:
        """записываем юзера в бд"""

        user_model = UserTable(
            username=user.username, hashed_password=user.hashed_password
        )

        self.session.add(user_model)

        return user_model

    async def get_user_by_id(self, user_id: int) -> UserTable | None:
        """ищем юзера по айди"""
        query = select(UserTable).where(
            UserTable.id == user_id, UserTable.is_active == True
        )

        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return user_model

    async def get_user_by_username(self, username: str) -> UserTable | None:
        """ищем юзера по имени"""
        query = select(UserTable).where(
            UserTable.username == username, UserTable.is_active == True
        )

        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return user_model

    async def delete_by_id(self, user_id: int) -> bool:
        """мягкое удаление по юзер айди"""
        query = select(UserTable).where(
            UserTable.id == user_id, UserTable.is_active == True
        )

        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return False

        user_model.is_active = False

        return True

    async def change_username(
        self, user_id: int, new_username: str
    ) -> UserTable | None:
        """меняем юзернейм, так как самый частый сценарий
        в изменениях модели пользователя - изменение юзернейма"""
        query = select(UserTable).where(
            UserTable.id == user_id, UserTable.is_active == True
        )
        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        user_model.username = new_username

        return user_model
