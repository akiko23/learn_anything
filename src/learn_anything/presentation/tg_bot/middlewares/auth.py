from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.filters import CommandObject
from aiogram.types import Message, CallbackQuery, TelegramObject
from dishka import AsyncContainer

from learn_anything.application.ports.auth.identity_provider import IdentityProvider


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

        command_obj: CommandObject | None = data.get('command', None)
        if command_obj and command_obj.command == 'start':
            return await handler(event, data)

        async with self._container(context={TelegramObject: event}) as request_container:
            id_provider = await request_container.get(IdentityProvider)

            if not data.get('user_role'):
                user_role = await id_provider.get_current_user_role()
                if user_role is None:
                    await msg.answer('Вы не авторизованы. Введите /start для корректной работы с ботом')
                    return

                data['user_role'] = user_role
            return await handler(event, data)
