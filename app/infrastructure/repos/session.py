from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def async_engine(db_url) -> AsyncEngine:
    return create_async_engine(
        db_url,
        pool_pre_ping=True,
        echo=False,
    )


def async_session(aengine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(aengine, expire_on_commit=False, class_=AsyncSession)
