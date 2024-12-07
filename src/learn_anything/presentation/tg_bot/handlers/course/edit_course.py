from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from dishka import FromDishka

from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.application.interactors.course.update_course import UpdateCourseInteractor, UpdateCourseInputData
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.domain.course.models import CourseID
from learn_anything.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException
from learn_anything.presentation.tg_bot.states.course import EditCourseForm
from learn_anything.presentors.tg_bot.keyboards.course.edit_course import get_course_edit_menu_kb, \
    get_course_after_edit_menu_kb, CANCEL_EDITING_KB
from learn_anything.presentors.tg_bot.texts.get_course import get_single_course_text

router = Router()


@router.callback_query(F.data.startswith('edit_course-'))
async def get_course_edit_menu(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetCourseInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
        file_manager: FromDishka[FileManager],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    target_course = await interactor.execute(
        data=GetCourseInputData(
            course_id=CourseID(int(course_id))
        )
    )

    text = get_single_course_text(course_data=target_course)
    text += '\n\nВыберите, что хотите изменить'

    kb = get_course_edit_menu_kb(
        course=target_course,
        back_to=back_to,
    )

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if target_course.photo_id:
        photo_id = target_course.photo_id
        photo_path = target_course.photo_path

    try:
        return await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=kb,
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=kb,
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=target_course.id
            ),
            collection_key=back_to,
        )


@router.callback_query(F.data.startswith('edit_course_title'))
async def start_editing_course_title(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    back_to, course_id = callback_query.data.split('-')[1:]
    await state.update_data(
        back_to=back_to,
        course_id=course_id
    )

    await callback_query.answer()

    await state.set_state(state=EditCourseForm.get_title)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новый заголовок', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(EditCourseForm.get_title), F.text)
async def edit_course_title(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to = data['course_id'], data['back_to']
    value = msg.text

    await interactor.execute(
        data=UpdateCourseInputData(
            course_id=CourseID(int(course_id)),
            title=value
        )
    )
    await state.set_state(state=None)

    await bot.send_message(
        chat_id=user_id,
        text='Заголовок успешно обновлен',
        reply_markup=get_course_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(F.data.startswith('edit_course_description'))
async def start_editing_course_description(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    back_to, course_id = callback_query.data.split('-')[1:]
    await state.update_data(
        back_to=back_to,
        course_id=course_id
    )

    await callback_query.answer()

    await state.set_state(state=EditCourseForm.get_description)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новое описание', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(EditCourseForm.get_description), F.text)
async def edit_course_description(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to = data['course_id'], data['back_to']
    value = msg.text

    await interactor.execute(
        data=UpdateCourseInputData(
            course_id=CourseID(int(course_id)),
            description=value
        )
    )
    await state.set_state(state=None)

    await bot.send_message(
        chat_id=user_id,
        text='Описание успешно обновлено',
        reply_markup=get_course_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(StateFilter(EditCourseForm), F.data == 'cancel_course_editing')
async def cancel_course_editing(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.set_state(state=None)

    course_id, back_to = data['course_id'], data['back_to']

    await bot.send_message(
        chat_id=user_id,
        text='Вы отменили процесс изменения',
        reply_markup=get_course_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(F.data.startswith('edit_course_photo'))
async def start_editing_course_photo(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    back_to, course_id = callback_query.data.split('-')[1:]
    await state.update_data(
        back_to=back_to,
        course_id=course_id
    )

    await callback_query.answer()

    await state.set_state(state=EditCourseForm.get_photo)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новое фото', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(EditCourseForm.get_photo), F.photo)
async def edit_course_photo(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to = data['course_id'], data['back_to']

    photo_id = msg.photo[-1].file_id
    photo = await bot.download(file=photo_id)

    await interactor.execute(
        data=UpdateCourseInputData(
            course_id=CourseID(int(course_id)),
            photo_id=photo_id,
            photo=photo,
        )
    )
    await state.set_state(state=None)

    await bot.send_message(
        chat_id=user_id,
        text='Фото успешно обновлено',
        reply_markup=get_course_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )
