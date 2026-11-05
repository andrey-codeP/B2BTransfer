from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from typing import Annotated, AsyncGenerator

from app.database.connection import async_session
from app.database.uow import UnitOfWork


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """зависемость - генератор выдающий сесии"""
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_uow(session: SessionDep) -> UnitOfWork:
    """зависемость выдающая uow"""
    return UnitOfWork(session)


UOWDep = Annotated[UnitOfWork, Depends(get_uow)]
