import logging
from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,  # type: ignore[override]
            data: dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            user_message = event.data
        else:
            user_id = event.chat.id
            user_message = event.text

        state: FSMContext = data['state']

        logger.info(
            '{ "user": %s, message: "%s", "state": { "context" : %s }',
            user_id,
            user_message,
            await state.get_state(),
        )

        await handler(event, data)
