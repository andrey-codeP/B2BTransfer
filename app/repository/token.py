from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from datetime import datetime, timedelta, timezone

from app.exceptions.token_exception import InvalidTokenError
from app.database.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_refresh_token(
        self, refresh_token: str, user_id: int, expire_at: datetime
    ) -> RefreshToken:
        """записываем токен в бд"""

        token = RefreshToken(
            refresh_token=refresh_token,
            expires_at=expire_at,
            user_id=user_id,
        )

        self.session.add(token)
        await self.session.flush()

        return token

    async def delete_refresh_token(self, hashed_token: str) -> None:
        """удаляет рефреш токен из бд"""
        query = delete(RefreshToken).where(RefreshToken.refresh_token == hashed_token)
        await self.session.execute(query)

    async def expire_token_soon(self, hashed_token: str, seconds: int = 10) -> None:
        """
        grace period: оставляем старый токен валидным на 10 секунд,
        чтобы параллельные запросы с фронтенда не получили 401
        """
        grace_expire = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        query = (
            update(RefreshToken)
            .where(
                RefreshToken.refresh_token == hashed_token,
                RefreshToken.expires_at > grace_expire,
            )
            .values(expires_at=grace_expire)
        )
        await self.session.execute(query)

    async def get_refresh_token(self, hashed_token: str) -> RefreshToken:
        """поулчаем хешированный токен и по нему ищем экземпляр в таблице"""
        query = select(RefreshToken).where(RefreshToken.refresh_token == hashed_token)
        result = await self.session.execute(query)
        token = result.scalar_one_or_none()

        if token is None:
            raise InvalidTokenError

        return token
