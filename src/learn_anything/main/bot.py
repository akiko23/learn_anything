import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from dishka.integrations.aiogram import setup_dishka

from learn_anything.adapters.auth.tg_auth import TgIdentityProvider
from learn_anything.adapters.persistence.tables.map import map_tables
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.presentation.tg_bot.config import load_bot_config
from learn_anything.presentation.tg_bot.handlers import register_handlers
from learn_anything.adapters.bootstrap.di import setup_di, TgProvider
from learn_anything.presentation.tg_bot.middlewares.__logging import LoggingMiddleware
from learn_anything.presentation.tg_bot.middlewares.auth import AuthMiddleware


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s: %(message)s'
    )

    container = setup_di()

    dp = Dispatcher(
        events_isolation=SimpleEventIsolation()
    )

    dp.message.middleware.register(AuthMiddleware(container))
    dp.callback_query.outer_middleware.register(AuthMiddleware(container))
    dp.message.outer_middleware.register(LoggingMiddleware())
    dp.callback_query.outer_middleware.register(LoggingMiddleware())

    setup_dishka(container=container, router=dp, auto_inject=True)

    map_tables()
    register_handlers(dp)

    bot_cfg = load_bot_config()

    await dp.start_polling(Bot(token=bot_cfg.token))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.exception("Bot was stopped!")
