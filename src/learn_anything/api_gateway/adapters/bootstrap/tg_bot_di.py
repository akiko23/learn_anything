import os

from aio_pika import Connection
from aio_pika.abc import AbstractChannel
from aio_pika.pool import Pool
from aiogram import Bot, Dispatcher
from aiogram.enums import MessageEntityType
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import TelegramObject, Message
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)

from learn_anything.api_gateway.adapters.rmq.config import load_rmq_config, RMQConfig
from learn_anything.api_gateway.adapters.rmq.providers import get_connection_pool, get_channel
from learn_anything.api_gateway.presentation.tg_bot.config import load_bot_config, BotConfig
from learn_anything.api_gateway.presentation.web.config import load_web_config, WebConfig

# DB + Redis imports (shared with course_platform for IDE queries)
from learn_anything.course_platform.adapters.persistence.config import load_db_config, DatabaseConfig
from learn_anything.course_platform.adapters.persistence.providers import (
    get_engine,
    get_async_sessionmaker,
    get_async_session,
)
from learn_anything.course_platform.adapters.persistence.tables.map import map_tables
from learn_anything.course_platform.adapters.redis.config import load_redis_config, RedisConfig


DEFAULT_API_GATEWAY_CONFIG_PATH = 'configs/api_gateway.toml'


def infrastructure_provider() -> Provider:
    provider = Provider()

    return provider


def configs_provider(cfg_path: str) -> Provider:
    provider = Provider()

    provider.provide(lambda: load_bot_config(cfg_path), scope=Scope.APP, provides=BotConfig)
    provider.provide(lambda: load_rmq_config(cfg_path), scope=Scope.APP, provides=RMQConfig)
    provider.provide(lambda: load_web_config(cfg_path), scope=Scope.APP, provides=WebConfig)

    return provider


def db_configs_provider(cfg_path: str) -> Provider:
    """Provides DB and Redis configs for IDE queries (read from course_platform config section)."""
    provider = Provider()

    # The api_gateway config doesn't have [db]/[redis] sections normally.
    # We read them from an optional env-overridden course_platform config path.
    cp_cfg_path = os.getenv('COURSE_PLATFORM_CONFIG_PATH') or 'configs/course_platform.toml'

    try:
        provider.provide(lambda: load_db_config(cp_cfg_path), scope=Scope.APP, provides=DatabaseConfig)
        provider.provide(lambda: load_redis_config(cp_cfg_path), scope=Scope.APP, provides=RedisConfig)
    except Exception:
        pass  # IDE queries will fail gracefully if DB not configured

    return provider


def db_provider() -> Provider:
    provider = Provider()
    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(get_async_session, scope=Scope.REQUEST)
    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, obj: TelegramObject) -> int:
        return obj.from_user.id  # type: ignore[attr-defined, no-any-return, unused-ignore]

    @provide(scope=Scope.REQUEST)
    async def get_command(self, obj: TelegramObject) -> str | None:
        if not isinstance(obj, Message) or not obj.entities:
            return None

        for entity in obj.entities:
            if entity.type == MessageEntityType.BOT_COMMAND:
                return obj.text
        return None

    @provide(scope=Scope.APP)
    async def get_bot(
            self,
            bot_cfg: BotConfig,
    ) -> Bot:
        return Bot(token=bot_cfg.token)

    @provide(scope=Scope.APP)
    async def get_dp(
            self,
    ) -> Dispatcher:
        dp = Dispatcher(
            events_isolation=SimpleEventIsolation()
        )
        return dp


def rmq_provider() -> Provider:
    provider = Provider()

    provider.provide(get_connection_pool, provides=Pool[Connection], scope=Scope.APP)
    provider.provide(get_channel, provides=AbstractChannel, scope=Scope.REQUEST)

    return provider


def setup_db_providers() -> list[Provider]:
    """Expose DB providers for external use."""
    return [db_provider()]


def setup_providers(cfg_path: str) -> list[Provider]:
    providers = [
        infrastructure_provider(),
        configs_provider(cfg_path),
        db_configs_provider(cfg_path),
        db_provider(),
        rmq_provider(),
        TgProvider(),
    ]
    return providers


def setup_di(cfg_path: str | None = None) -> AsyncContainer:
    if cfg_path is None:
        cfg_path = os.getenv('API_GATEWAY_CONFIG_PATH') or DEFAULT_API_GATEWAY_CONFIG_PATH

    # Expose BOT_TOKEN env for IDE router's HMAC verification
    try:
        bot_cfg = load_bot_config(cfg_path)
        os.environ['BOT_TOKEN'] = bot_cfg.token
    except Exception:
        pass

    # Map ORM tables (needed for IDE task queries)
    try:
        map_tables()
    except Exception:
        pass

    providers = setup_providers(cfg_path)
    container = make_async_container(*providers)
    return container
