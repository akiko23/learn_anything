import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast

import msgpack
import uvicorn
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, ExchangeType
from aiogram import Dispatcher, Bot
from aiogram.types import Update
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from fastapi import FastAPI

from learn_anything.course_platform.adapters.bootstrap.tg_bot_di import setup_di, DEFAULT_COURSE_PLATFORM_CONFIG_PATH
from learn_anything.course_platform.adapters.logger import logger, correlation_id_ctx, LOGGING_CONFIG
from learn_anything.course_platform.adapters.metrics import TOTAL_MESSAGES_CONSUMED
from learn_anything.course_platform.adapters.persistence.tables.map import map_tables
from learn_anything.course_platform.presentation.bg_tasks import background_tasks
from learn_anything.course_platform.presentation.tg_bot.handlers import register_handlers
from learn_anything.course_platform.presentation.tg_bot.middlewares.__logging import LoggingMiddleware
from learn_anything.course_platform.presentation.tg_bot.middlewares.auth import AuthMiddleware
from learn_anything.course_platform.presentation.web.config import load_web_config
from learn_anything.course_platform.presentation.web.fastapi_routers.tech import router

RETRIES_NUMBER = 5


async def callback(msg: AbstractIncomingMessage, dp: Dispatcher, bot: Bot) -> None:
    if msg.correlation_id:
        correlation_id_ctx.set(msg.correlation_id)

    update_dct = msgpack.unpackb(msg.body)
    logger.info('Processing update..')
    update = Update.model_validate(update_dct)

    for _ in range(RETRIES_NUMBER):
        try:
            await dp.feed_update(bot=bot, update=update)
            await msg.ack()
            return
        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(1.5)  # no spamming
        finally:
            TOTAL_MESSAGES_CONSUMED.inc()

    await msg.reject()


async def start_consumer(container: AsyncContainer) -> None:
    queue_name = "tg_updates"

    dp = await container.get(Dispatcher)
    dp.message.middleware.register(AuthMiddleware(container))
    dp.callback_query.outer_middleware.register(AuthMiddleware(container))

    dp.message.outer_middleware(LoggingMiddleware())
    dp.callback_query.outer_middleware(LoggingMiddleware())

    setup_dishka(container=container, router=dp, auto_inject=True)

    map_tables()
    register_handlers(dp)

    bot = await container.get(Bot)
    async with container() as request_container:
        channel = await request_container.get(AbstractChannel)

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue
        exchange = await channel.declare_exchange("tg_updates", ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(name=queue_name, durable=True)
        await queue.bind(
            exchange,
            queue_name,
        )

        logger.info('Starting consumer')
        async for message in queue.iterator():
            process_update_task = asyncio.create_task(callback(cast(AbstractIncomingMessage, message), dp, bot))
            process_update_task.add_done_callback(background_tasks.discard)

            background_tasks.add(
                process_update_task
            )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info('Starting lifespan')

    logger.info('Setup ioc')
    container = setup_di()

    task = asyncio.create_task(start_consumer(container))

    logger.info('Started successfully')
    yield

    if task is not None:
        logger.info("Stopping polling...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Polling stopped")

    logger.info('Ending lifespan')


def create_app() -> FastAPI:
    logging.config.dictConfig(LOGGING_CONFIG)

    web_cfg = load_web_config(
        config_path=os.getenv('COURSE_PLATFORM_CONFIG_PATH') or DEFAULT_COURSE_PLATFORM_CONFIG_PATH
    )
    app = FastAPI(
        title=web_cfg.title,
        description=web_cfg.description,
        docs_url='/docs',
        lifespan=lifespan
    )
    app.include_router(router, prefix='', tags=['tech'])

    return app


async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

    web_cfg = load_web_config(
        config_path=os.getenv('COURSE_PLATFORM_CONFIG_PATH') or DEFAULT_COURSE_PLATFORM_CONFIG_PATH
    )
    uvicorn_config = uvicorn.Config(
        'learn_anything.course_platform.main.consumer:create_app',
        factory=True,
        host=web_cfg.host,
        port=web_cfg.port,
        workers=1
    )
    server = uvicorn.Server(uvicorn_config)

    logger.info('Starting server..')
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
