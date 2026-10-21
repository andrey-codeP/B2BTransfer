from app.database.connection import async_session

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from typing import Annotated, AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """зависемость для выдачи сессий"""
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
