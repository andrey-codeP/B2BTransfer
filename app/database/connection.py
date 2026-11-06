from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

# настраиваем подключение к постгрес, выдачу сессий и движок

DATABASE_URL = settings.POSTGRES_URL

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
