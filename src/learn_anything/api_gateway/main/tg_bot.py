import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from aiogram import Dispatcher, Bot
from dishka.integrations.fastapi import setup_dishka as fastapi_setup_dishka
from fastapi import FastAPI
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from learn_anything.api_gateway.adapters.bootstrap.tg_bot_di import setup_di
from learn_anything.api_gateway.adapters.logger import LOGGING_CONFIG, logger
from learn_anything.api_gateway.presentation.tg_bot.config import BotConfig
from learn_anything.api_gateway.presentation.web.fastapi_routers.tech import router as tech_router
from learn_anything.api_gateway.presentation.web.fastapi_routers.tg import router as tg_router
from learn_anything.api_gateway.presentation.tg_bot.middlewares.__logging import LoggingMiddleware
from learn_anything.api_gateway.presentation.tg_bot.middlewares.count_rps import RequestCountMiddleware
from learn_anything.api_gateway.presentation.tg_bot.middlewares.send_to_queue import SendToQueueMiddleware


@asynccontextmanager
async def lifespan(
        app: FastAPI,
) -> AsyncGenerator[None, None]:
    logger.info('Starting lifespan')

    container = app.state.dishka_container
    bot_cfg = await container.get(BotConfig)
    bot = await container.get(Bot)

    dp: Dispatcher = await container.get(Dispatcher)
    dp.message.outer_middleware.register(LoggingMiddleware())
    dp.callback_query.outer_middleware.register(LoggingMiddleware())

    polling_task: asyncio.Task[None] | None = None
    if bot_cfg.bot_webhook_url:
        logger.info('Start webhook on %s', bot_cfg.bot_webhook_url)
        await bot.set_webhook(bot_cfg.bot_webhook_url)
    else:
        dp.update.middleware(SendToQueueMiddleware(container=container))
        polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))

    logger.info('Finished start')
    yield

    if polling_task is not None:
        logger.info("Stopping polling...")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            logger.info("Polling stopped")

    await bot.delete_webhook()
    logger.info('Ending lifespan')


def create_app() -> FastAPI:
    app = FastAPI(docs='/docs', lifespan=lifespan)

    app.include_router(tg_router, prefix='/tg', tags=['tg'])
    app.include_router(tech_router, prefix='/tech', tags=['tech'])

    app.middleware("http")(RequestCountMiddleware())

    container = setup_di()
    fastapi_setup_dishka(container=container, app=app)

    app.add_middleware(RawContextMiddleware, plugins=[plugins.CorrelationIdPlugin()])
    return app


async def main():
    logging.config.dictConfig(LOGGING_CONFIG)

    uvicorn_config = uvicorn.Config(
        'api_gateway.main.tg_bot:create_app',
        factory=True,
        host='0.0.0.0',
        port=8080,
        workers=1
    )
    server = uvicorn.Server(uvicorn_config)
    logger.info('Starting server..')
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.exception("Bot was stopped with err!")
    else:
        logger.info("Bot was successfully stopped")