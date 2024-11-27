import logging
from typing import cast

from aiogram import Bot
from aiogram.types import Message, ErrorEvent, BufferedInputFile

from learn_anything.entities.error import ApplicationError
from learn_anything.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException

logger = logging.getLogger(__name__)


async def load_media_if_not_exists(
        event: ErrorEvent,
        msg: Message,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    exc: NoMediaOnTelegramServersException = cast(NoMediaOnTelegramServersException, event.exception)
    update_interactor = exc.update_interactor
    input_data = exc.interactor_input_data

    logger.error('Telegram deleted media from its servers. Uploading new..')

    msg = await bot.send_photo(
        chat_id=user_id,
        photo=BufferedInputFile(exc.media_buffer.read(), 'stub'),
        caption=exc.text_to_send,
        reply_markup=exc.keyboard,
    )

    new_photo_id = msg.photo[-1].file_id
    new_photo = await bot.download(new_photo_id)

    input_data.photo_id = new_photo_id
    input_data.photo = new_photo
    await update_interactor.execute(
        data=input_data
    )


async def handle_user_error(
        event: ErrorEvent, msg: Message
):
    user_id: int = msg.from_user.id
    err: ApplicationError = cast(ApplicationError, event.exception)

    logger.info('User with id=%d got error: \'%s\'', user_id, err.message)
    await msg.answer(err.message)


async def exception_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)
