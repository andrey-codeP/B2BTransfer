from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from httpx import AsyncClient, ASGITransport
import pytest

from app.security.login import TokenManager
from app.database.dependencies.depends import get_session
from app.main import app
from app.config import settings
from app.database.models.base import Base
from app.database.models import (
    TransferTable,
    WalletTable,
    UserTable,
    HistoryTransferTable,
)

password = settings.POSTGRES_PASSWORD
user = settings.POSTGRES_USER


DATABASE_URL = "postgresql+asyncpg://test:test@127.0.0.1:5433/test"


@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(DATABASE_URL)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_test_session(engine, setup_database):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
        )
        session = session_factory()
        await session.begin_nested()
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture
async def test_client(db_test_session):
    async def override_get_session():
        yield db_test_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[TokenManager.get_id_by_access_token] = lambda: 67

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
