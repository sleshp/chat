from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

Base = declarative_base()


def get_engine(database_url: str = None):
    url = database_url or settings.database_url
    return create_async_engine(url, future=True)


def get_sessionmaker(engine=None):
    if engine is None:
        engine = get_engine()
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


engine = get_engine()
async_session = get_sessionmaker(engine)
