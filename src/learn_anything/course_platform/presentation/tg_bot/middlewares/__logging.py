import logging
from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger('api_gateway_logger')


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,  # type: ignore[override]
            data: dict[str, Any],
    ) -> Any:
        user_id: int = event.from_user.id if isinstance(event, CallbackQuery) else event.chat.id
        user_input = f'callback_data: {event.data}' if isinstance(event, CallbackQuery) else f'msg_text: {event.text}'
        state: FSMContext = data['state']

        logger.info(
            'Request from user with id=%s; input={ %s }; state=%s',
            user_id,
            user_input,
            await state.get_state(),
        )
        logger.debug(
            '{ "user": %s, input: { %s }, "state": { "context" : %s, data: %s }',
            user_id,
            user_input,
            await state.get_state(),
            await state.get_data()
        )

        await handler(event, data)
