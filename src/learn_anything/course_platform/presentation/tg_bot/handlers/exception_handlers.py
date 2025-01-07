from contextlib import suppress
from typing import cast, Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent, BufferedInputFile, InputMediaPhoto
from dishka import FromDishka

from learn_anything.course_platform.adapters.logger import logger
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.domain.error import ApplicationError
from learn_anything.course_platform.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException


async def load_media_if_not_exists(
        event: ErrorEvent,
        msg: Message,
        state: FSMContext,
        bot: Bot,
        file_manager: FromDishka[FileManager],
) -> None:
    data = await state.get_data()

    user_id: int = msg.chat.id
    exc: NoMediaOnTelegramServersException = cast(NoMediaOnTelegramServersException, event.exception)
    update_interactor = exc.update_interactor
    input_data = exc.interactor_input_data

    logger.warning('No media found on telegram servers. Uploading new with path %s', exc.media_path)

    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=user_id, message_id=msg.message_id)

    media_buffer = await file_manager.get_by_file_path(file_path=exc.media_path)
    if media_buffer is None:
        raise FileNotFoundError(f'No such file path: \'{exc.media_path}\'')

    media_content = media_buffer.read()
    try:
        msg = cast(Message, await bot.edit_message_media(
            chat_id=user_id,
            message_id=msg.message_id,
            media=InputMediaPhoto(
                media=BufferedInputFile(media_content, 'stub'),
                caption=exc.text_to_send,
            ),
            reply_markup=exc.keyboard,
        ))
    except TelegramBadRequest:
        logger.info(media_content)
        msg = cast(Message, await bot.send_photo(
            chat_id=user_id,
            photo=BufferedInputFile(media_content, 'stub'),
            caption=exc.text_to_send,
            reply_markup=exc.keyboard,
        ))

    new_photo_id = msg.photo[-1].file_id  # type: ignore[index]

    # if media in defaults we just need to update its tag in storage
    if 'defaults' in exc.media_path:
        await file_manager.update(
            old_file_path=exc.media_path,
            payload=None,
            new_file_path=file_manager.generate_path(('defaults',), new_photo_id)
        )
        return

    input_data.photo_id = new_photo_id
    input_data.photo = media_buffer
    await update_interactor.execute(
        data=input_data
    )

    collection = data[exc.collection_key]
    collection[data[f'{exc.collection_key}_pointer']].photo_id = new_photo_id

    await state.update_data(
        {exc.collection_key: collection}
    )


async def handle_user_error(
        event: ErrorEvent, msg: Message
) -> None:
    user_id: int = msg.chat.id
    err: ApplicationError = cast(ApplicationError, event.exception)

    logger.info('User with id=%d got error: \'%s\'', user_id, err.message)
    await msg.answer(err.message)


async def exception_handler(
        event: ErrorEvent,
        msg: Message,
        user_message: str,

        state: FSMContext,
) -> None:
    user_id: int = msg.chat.id
    state_data: dict[str, Any] = await state.get_data()

    logger.critical("Critical error caused by %s", event.exception, exc_info=True)
    logger.critical(
        '{ "user": %s, message: "%s", "state": { "context" : %s, data: %s }',
        user_id,
        user_message,
        await state.get_state(),
        state_data
    )
    raise event.exception
