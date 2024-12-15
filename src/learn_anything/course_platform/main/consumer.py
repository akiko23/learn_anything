import asyncio
import logging
from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncGenerator

import msgpack
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, ExchangeType
from aiogram import Dispatcher, Bot
from aiogram.types import Update
from dishka.integrations.aiogram import setup_dishka
from fastapi import FastAPI

from learn_anything.course_platform.adapters.metrics import TOTAL_MESSAGES_CONSUMED
from learn_anything.course_platform.adapters.bootstrap.tg_bot_di import setup_di
from learn_anything.course_platform.adapters.consumer.logger import logger, correlation_id_ctx, LOGGING_CONFIG
from learn_anything.course_platform.adapters.persistence.tables.map import map_tables
from learn_anything.course_platform.presentation.tg_bot.handlers import register_handlers
from learn_anything.course_platform.presentation.tg_bot.middlewares.auth import AuthMiddleware
from learn_anything.course_platform.presentation.web.fastapi_routers.tech import router


async def callback(dp: Dispatcher, bot: Bot, msg: AbstractIncomingMessage):
    correlation_id_ctx.set(msg.correlation_id)
    logger.info('Processing msg')

    update = Update.model_validate(msgpack.unpackb(msg.body))
    await dp.feed_update(bot=bot, update=update)

    await msg.ack()
    TOTAL_MESSAGES_CONSUMED.inc()


async def start_consumer(channel: AbstractChannel, dp: Dispatcher, bot: Bot) -> None:
    queue_name = "tg_updates"

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
    await queue.consume(callback=partial(callback, dp, bot))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info('Starting lifespan')

    container = setup_di()

    dp = await container.get(Dispatcher)
    dp.message.middleware.register(AuthMiddleware(container))
    dp.callback_query.outer_middleware.register(AuthMiddleware(container))

    logger.info('Setup ioc')
    setup_dishka(container=container, router=dp, auto_inject=True)

    map_tables()
    register_handlers(dp)

    bot = await container.get(Bot)
    async with container() as request_container:
        channel = await request_container.get(AbstractChannel)
        task = asyncio.create_task(start_consumer(dp=dp, bot=bot, channel=channel))

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

    app = FastAPI(docs_url='/docs', lifespan=lifespan)
    app.include_router(router, prefix='', tags=['tech'])

    return app
