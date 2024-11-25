import logging
from typing import cast

from aiogram.types import Message, ErrorEvent

from learn_anything.entities.error import ApplicationError

logger = logging.getLogger(__name__)


async def handle_user_error(
        event: ErrorEvent, msg: Message
):
    user_id: int = msg.from_user.id
    err: ApplicationError = cast(ApplicationError, event.exception)

    logger.info('User with id=%d got error: \'%s\'', user_id, err.message)
    await msg.answer(err.message)


async def exception_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)
