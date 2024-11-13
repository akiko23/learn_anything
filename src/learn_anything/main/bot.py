import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)
from dishka.integrations.aiogram import setup_dishka

from learn_anything.adapters.persistence.tables.map import map_tables
from learn_anything.presentation.bot.config import load_bot_config
from learn_anything.presentation.bot.handlers import register_handlers
from learn_anything.adapters.bootstrap.di import setup_di


async def main():
    logging.basicConfig(level=logging.INFO)

    container = setup_di()

    dp = Dispatcher(
        events_isolation=SimpleEventIsolation()
    )

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
