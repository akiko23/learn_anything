import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from aio_pika import Connection
from aio_pika.pool import Pool
from aiogram import Dispatcher, Bot
from dishka import FromDishka
from dishka.integrations.aiogram import setup_dishka
from dishka.integrations.fastapi import setup_dishka as fastapi_setup_dishka
from fastapi import FastAPI
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from learn_anything.adapters.bootstrap.tg_bot_di import setup_di
from learn_anything.adapters.persistence.tables.map import map_tables
from learn_anything.adapters.rmq.initialisers import init_rabbitmq
from learn_anything.presentation.bg_tasks import background_tasks
from learn_anything.presentation.tg_bot.config import BotConfig
from learn_anything.presentation.tg_bot.fastapi_routers.tech import router as tech_router
from learn_anything.presentation.tg_bot.fastapi_routers.tg import router as tg_router
from learn_anything.presentation.tg_bot.handlers import register_handlers
from learn_anything.presentation.tg_bot.middlewares.__logging import LoggingMiddleware
from learn_anything.presentation.tg_bot.middlewares.auth import AuthMiddleware
from learn_anything.presentation.tg_bot.middlewares.count_rps import RequestCountMiddleware


@asynccontextmanager
async def lifespan(
        _: FastAPI,
        bot_cfg: FromDishka[BotConfig],
        bot: FromDishka[Bot],
        dp: FromDishka[Dispatcher],
) -> AsyncGenerator[None, None]:
    logging.info('Starting lifespan')

    if bot_cfg.bot_webhook_url:
        await bot.set_webhook(bot_cfg.bot_webhook_url)
    else:
        await dp.start_polling(Bot(
            token=bot_cfg.token,
        ))

    temp = await bot.get_webhook_info()
    logging.info(temp)

    logging.info('Finished start')

    yield

    while background_tasks:
        await asyncio.sleep(0)
    await bot.delete_webhook()
    logging.info('Ending lifespan')


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/docs')

    container = setup_di()
    fastapi_setup_dishka(container=container, app=app)

    app.lifespan = lifespan

    app.include_router(tg_router, prefix='/tg', tags=['tg'])
    app.include_router(tech_router, prefix='/tech', tags=['tech'])

    app.middleware("http")(RequestCountMiddleware())
    app.add_middleware(RawContextMiddleware, plugins=[plugins.CorrelationIdPlugin()])
    return app


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s %(asctime)s: %(message)s'
    )

    container = setup_di()

    dp = await container.get(Dispatcher)
    dp.message.middleware.register(AuthMiddleware(container))
    dp.callback_query.outer_middleware.register(AuthMiddleware(container))
    dp.message.outer_middleware.register(LoggingMiddleware())
    dp.callback_query.outer_middleware.register(LoggingMiddleware())

    setup_dishka(container=container, router=dp, auto_inject=True)

    connection_pool = await container.get(Pool[Connection])
    await init_rabbitmq(connection_pool)

    map_tables()
    register_handlers(dp)

    uvicorn_config = uvicorn.Config(
        'learn_anything.main.tg_bot:create_app',
        factory=True,
        host='0.0.0.0',
        port=8000,
        workers=1
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.exception("Bot was stopped with err!")
    else:
        logging.info("Bot was successfully stopped")
