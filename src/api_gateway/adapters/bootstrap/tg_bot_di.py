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

from api_gateway.adapters.rmq.config import load_rmq_config, RMQConfig
from api_gateway.adapters.rmq.manager import RMQManager
from api_gateway.adapters.rmq.providers import get_connection_pool, get_channel
from api_gateway.presentation.tg_bot.config import load_bot_config, BotConfig


def infrastructure_provider() -> Provider:
    provider = Provider()

    provider.provide(RMQManager, scope=Scope.REQUEST)
    return provider


def configs_provider() -> Provider:
    provider = Provider()

    provider.provide(lambda: load_bot_config(), scope=Scope.APP, provides=BotConfig)
    provider.provide(lambda: load_rmq_config(), scope=Scope.APP, provides=RMQConfig)

    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, obj: TelegramObject) -> int:
        return obj.from_user.id

    @provide(scope=Scope.REQUEST)
    async def get_command(self, obj: TelegramObject) -> str | None:
        if not isinstance(obj, Message) or not obj.entities:
            return None

        for entity in obj.entities:
            if entity.type == MessageEntityType.BOT_COMMAND:
                return obj.text

    @provide(scope=Scope.APP)
    async def get_bot(
            self,
            bot_cfg: BotConfig,
    ) -> Bot:
        return Bot(token=bot_cfg.token)

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


def setup_providers() -> list[Provider]:
    providers = [
        infrastructure_provider(),
        configs_provider(),
        rmq_provider(),
        TgProvider()
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    container = make_async_container(*providers)

    return container
