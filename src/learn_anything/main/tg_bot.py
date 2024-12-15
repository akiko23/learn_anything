import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from aiogram import Dispatcher, Bot
from dishka.integrations.aiogram import setup_dishka
from dishka.integrations.fastapi import setup_dishka as fastapi_setup_dishka
from fastapi import FastAPI
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api_gateway.adapters.logger import LOGGING_CONFIG
from learn_anything.adapters.bootstrap.tg_bot_di import setup_di
from learn_anything.adapters.persistence.tables.map import map_tables
from learn_anything.presentation.bg_tasks import background_tasks
from learn_anything.presentation.tg_bot.config import BotConfig
from learn_anything.presentation.web.fastapi_routers.tech import router as tech_router
from learn_anything.presentation.tg_bot.handlers import register_handlers
from learn_anything.presentation.tg_bot.middlewares.__logging import LoggingMiddleware
from learn_anything.presentation.tg_bot.middlewares.auth import AuthMiddleware


@asynccontextmanager
async def lifespan(
        app: FastAPI,
) -> AsyncGenerator[None, None]:
    logging.info('Starting lifespan')

    container = app.state.dishka_container
    bot_cfg = await container.get(BotConfig)
    bot = await container.get(Bot)

    dp = await container.get(Dispatcher)
    dp.message.middleware.register(AuthMiddleware(container))
    dp.callback_query.outer_middleware.register(AuthMiddleware(container))
    dp.message.outer_middleware.register(LoggingMiddleware())
    dp.callback_query.outer_middleware.register(LoggingMiddleware())

    logging.info('Setup aiogram dishka')
    setup_dishka(container=container, router=dp, auto_inject=True)

    map_tables()
    register_handlers(dp)

    polling_task: asyncio.Task[None] | None = None
    if bot_cfg.bot_webhook_url:
        logging.info('Start webhook on %s', bot_cfg.bot_webhook_url)
        await bot.set_webhook(bot_cfg.bot_webhook_url)
    else:
        polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))

    logging.info('Finished start')
    yield

    if polling_task is not None:
        logging.info("Stopping polling...")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            logging.info("Polling stopped")

    while background_tasks:
        await asyncio.sleep(0)
    await bot.delete_webhook()
    logging.info('Ending lifespan')


def create_app() -> FastAPI:
    app = FastAPI(docs='/docs', lifespan=lifespan)
    app.include_router(tech_router, prefix='/tech', tags=['tech'])

    container = setup_di()
    fastapi_setup_dishka(container=container, app=app)

    app.add_middleware(RawContextMiddleware, plugins=[plugins.CorrelationIdPlugin()])
    return app


async def main():
    logging.config.dictConfig(LOGGING_CONFIG)

    uvicorn_config = uvicorn.Config(
        'learn_anything.main.tg_bot:create_app',
        factory=True,
        host='0.0.0.0',
        port=8080,
        workers=1
    )
    server = uvicorn.Server(uvicorn_config)
    logging.info('Starting server..')
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.exception("Bot was stopped with err!")
    else:
        logging.info("Bot was successfully stopped")
