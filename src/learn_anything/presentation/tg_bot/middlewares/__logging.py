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
        state_data: dict[str, Any] = await state.get_data()

        logger.info(
            '{ "user": %s, message: "%s", "state": { "context" : %s, "data": %s }',
            user_id,
            user_message,
            await state.get_state(),
            state_data
        )

        await handler(event, data)



