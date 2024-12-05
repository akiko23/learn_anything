import logging
from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user_id: int = event.from_user.id
        user_message = event.data if isinstance(event, CallbackQuery) else event.text
        state: FSMContext = data['state']

        logger.info(
            '{ "user": %s, message: "%s", "state": { "context" : %s }',
            user_id,
            user_message,
            await state.get_state(),
        )

        await handler(event, data)



