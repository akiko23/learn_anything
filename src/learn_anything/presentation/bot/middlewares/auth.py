from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.enums.message_entity_type import MessageEntityType


from dishka import AsyncContainer

from learn_anything.adapters.bootstrap.di import TgProvider
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.entities.user.errors import UserNotAuthenticatedError


class AuthMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer):
        self._container = container

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        msg = event.message if isinstance(event, CallbackQuery) else event

        if self._msg_is_command_start(msg):
            await data['state'].set_state(state=None)
            return await handler(msg, data)

        async with self._container(context={TelegramObject: event}) as request_container:
            id_provider = await request_container.get(IdentityProvider)

            if not data.get('user_role'):
                try:
                    user = await id_provider.get_user()
                    data['user_role'] = user.role
                except UserNotAuthenticatedError:
                    return await msg.answer('Вы не авторизованы. Введите /start для корректной работы с ботом')
            return await handler(event, data)

    def _msg_is_command_start(self, msg: Message) -> bool:
        if not msg.entities:
            return False

        msg_type = msg.entities[0].type
        if msg_type != MessageEntityType.BOT_COMMAND:
            return False

        if not msg.text:
            return False

        command, _ = self._parse_command(msg.text)
        return command == '/start'

    @staticmethod
    def _parse_command(text: str) -> tuple[str, str]:
        try:
            command, arg = text.split(maxsplit=1)
        except ValueError:
            command, arg = text, ""
        return command, arg
