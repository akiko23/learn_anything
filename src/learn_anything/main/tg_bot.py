import asyncio
import json
import logging
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from dishka.integrations.aiogram import setup_dishka

from learn_anything.adapters.bootstrap.tg_bot_di import setup_di
from learn_anything.adapters.persistence.tables.map import map_tables
from learn_anything.adapters.redis.config import RedisConfig
from learn_anything.adapters.json_serializers import DTOJSONEncoder, dto_obj_hook
from learn_anything.presentation.tg_bot.config import load_bot_config, BotConfig
from learn_anything.presentation.tg_bot.handlers import register_handlers
from learn_anything.presentation.tg_bot.middlewares.__logging import LoggingMiddleware
from learn_anything.presentation.tg_bot.middlewares.auth import AuthMiddleware


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s %(asctime)s: %(message)s'
    )

    container = setup_di()

    redis_cfg = await container.get(RedisConfig)

    storage = RedisStorage.from_url(
        url=redis_cfg.dsn,
        json_dumps=partial(json.dumps, cls=DTOJSONEncoder),
        json_loads=partial(json.loads, object_hook=dto_obj_hook),
    )
    dp = Dispatcher(
        events_isolation=SimpleEventIsolation(),
        storage=storage
    )

    dp.message.middleware.register(AuthMiddleware(container))
    dp.callback_query.outer_middleware.register(AuthMiddleware(container))
    dp.message.outer_middleware.register(LoggingMiddleware())
    dp.callback_query.outer_middleware.register(LoggingMiddleware())

    setup_dishka(container=container, router=dp, auto_inject=True)

    map_tables()
    register_handlers(dp)

    bot_cfg = await container.get(BotConfig)

    await dp.start_polling(Bot(token=bot_cfg.token))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.exception("Bot was stopped with err!")
    else:
        logging.info("Bot was successfully stopped")
