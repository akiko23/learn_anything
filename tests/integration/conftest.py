import asyncio
import os
from asyncio import CancelledError, AbstractEventLoop
from contextlib import suppress
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from aio_pika.abc import AbstractChannel
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
)

import learn_anything.course_platform.adapters.persistence.tables  # noqa
from learn_anything.course_platform.adapters.persistence.config import DatabaseConfig
from learn_anything.course_platform.adapters.persistence.tables import metadata
from learn_anything.course_platform.main.consumer import (
    setup_di, start_consumer
)

TEST_CONFIG_PATH = "configs/test_consumer.toml"
SETUP_TEST_ENVIRONMENT_SCRIPT_PATH = 'tests/integration/scripts/setup_test_environment.sh'
RM_TEST_ENVIRONMENT_SCRIPT_PATH = 'tests/integration/scripts/rm_test_environment.sh'


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def _prepare_test_environment():
    os.system(f'chmod +x {SETUP_TEST_ENVIRONMENT_SCRIPT_PATH} && ./{SETUP_TEST_ENVIRONMENT_SCRIPT_PATH}')
    yield
    os.system(f'chmod +x {RM_TEST_ENVIRONMENT_SCRIPT_PATH} && ./{RM_TEST_ENVIRONMENT_SCRIPT_PATH}')


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def ioc_container(_prepare_test_environment) -> AsyncContainer:
    os.environ['COURSE_PLATFORM_CONFIG_PATH'] = TEST_CONFIG_PATH
    container = setup_di()
    return container


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def engine(ioc_container: AsyncContainer) -> AsyncEngine:
    eng = await ioc_container.get(AsyncEngine)
    return eng


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def db_cfg(ioc_container: AsyncContainer) -> DatabaseConfig:
    cfg = await ioc_container.get(DatabaseConfig)
    return cfg


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def _make_migrations(engine: AsyncEngine, db_cfg: DatabaseConfig) -> None:
    async with engine.begin() as conn:
        await conn.execute(text('create schema if not exists test;'))
        await conn.execute(text('create extension if not exists "uuid-ossp";'))

        await conn.run_sync(metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def db_session(
        ioc_container: AsyncContainer, _make_migrations,
) -> AsyncGenerator[AsyncSession, None]:
    async with ioc_container() as request_container:
        session = await request_container.get(AsyncSession)
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope='module', loop_scope="session")
async def rmq_channel(ioc_container: AsyncContainer) -> AsyncGenerator[AbstractChannel, None]:
    async with ioc_container() as request_container:
        channel = await request_container.get(AbstractChannel)
        yield channel


@pytest_asyncio.fixture(scope='module', loop_scope="session")
async def _init_consumer(request, ioc_container: AsyncContainer) -> AsyncGenerator[
    None, None]:
    task = asyncio.create_task(start_consumer(ioc_container))
    yield
    with suppress(CancelledError, RuntimeError):
        task.cancel()
        await task


