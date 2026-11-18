from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import RefreshToken

from datetime import datetime


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_refresh_token(
        self, refresh_token: str, user_id: int, expire_at: datetime
    ) -> RefreshToken:
        """записываем токен в бд"""

        token = RefreshToken(
            refresh_token=refresh_token,
            expire_at=expire_at,
            user_id=user_id,
        )

        self.session.add(token)
        await self.session.flush()

        return token
