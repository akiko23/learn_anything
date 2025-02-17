import logging
from typing import AsyncGenerator, AsyncIterable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from learn_anything.course_platform.adapters.persistence.config import DatabaseConfig

logger = logging.getLogger(__name__)


async def get_engine(settings: DatabaseConfig) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        settings.db_url,
        future=True,
    )

    logger.info("Engine was created.")

    yield engine

    await engine.dispose()

    logger.info("Engine was disposed.")


async def get_async_sessionmaker(
        engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    logger.info("Session provider was initialized")

    return session_factory


async def get_async_session(
        session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterable[AsyncSession]:
    async with session_factory() as session:
        yield session
