from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from httpx import AsyncClient, ASGITransport
from fastapi import status
import pytest
import pytest_asyncio

from typing import AsyncGenerator
from dataclasses import dataclass

from app.database.dependencies.depends import get_session
from app.main import app
from app.database.models.base import Base
from app.database.models import (
    TransferTable,
    WalletTable,
    UserTable,
    HistoryTransferTable,
)


DATABASE_URL = "postgresql+asyncpg://test:test@127.0.0.1:5433/test"


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """создает пул соеденений к бд на протяжение всех тестов"""

    eng = create_async_engine(DATABASE_URL)
    try:
        yield eng
    finally:
        await eng.dispose()  # в конце на всякий удаляем сами соеденения


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(engine):
    """создает таблицы до тестов и удаляет после, при этом
    autouse гарантируется что фикстура начнет выполняться до первого теста"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создаем
    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.drop_all
            )  # удаляем, при этом даже если произошли исключения


@pytest_asyncio.fixture
async def session_factory(engine, setup_database):
    """создаем фабрику от engine на каждый тест"""

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@dataclass
class RegisteredUser:
    """модель юзера для тестов"""

    id: int
    headers: dict


@pytest_asyncio.fixture
async def registered_user(test_client, user_model) -> RegisteredUser:
    """фабрика которая регистрирует и логинит пользователя, отдает аксес токен с айди"""

    reg = await test_client.post("/auth/registry", json=user_model)
    assert reg.status_code == status.HTTP_201_CREATED
    user_id = reg.json()["id"]

    login = await test_client.post(
        "/auth/login",
        data={"username": user_model["username"], "password": user_model["password"]},
    )
    assert login.status_code == status.HTTP_200_OK
    token = login.json()["access_token"]

    return RegisteredUser(id=user_id, headers={"Authorization": f"Bearer {token}"})


@pytest_asyncio.fixture
async def test_client(session_factory):
    async def override_get_session():
        # я знаю что такой подход при большой паралельности приведет
        # к переполнению пула соеденений, но паралелизма у меня будет не много
        # каждая сессия выдается на каждый запрос
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_session, None)
        # модно было воспользоваться и clear, но я там пилил свои оверайды в тестах, перешл на pop
        # для точечного удаления, а теперь те оверайды заменил, но pop оставил


@pytest.fixture
def user_model() -> dict:
    return {"username": "олег228", "password": "228228228"}
