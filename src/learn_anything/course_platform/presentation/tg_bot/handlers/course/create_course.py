from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.course.create_course import CreateCourseInteractor, CreateCourseInputData
from learn_anything.course_platform.application.ports.data.file_manager import FileManager, COURSES_DEFAULT_DIRECTORY
from learn_anything.course_platform.domain.entities.user.models import UserRole
from learn_anything.course_platform.presentation.tg_bot.states.course import CreateCourseForm
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.create_course import CANCEL_COURSE_CREATION_KB, \
    GET_COURSE_PHOTO_KB, \
    GET_COURSE_REGISTRATIONS_LIMIT_KB
from learn_anything.course_platform.presentors.tg_bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.callback_query(F.data == 'main_menu-create_course')
async def start_course_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot
):
    user_id: int = callback_query.from_user.id

    await state.set_state(CreateCourseForm.get_title)

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    msg = await bot.send_message(chat_id=user_id, text='Введите название курса', reply_markup=CANCEL_COURSE_CREATION_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateCourseForm.get_title))
async def get_course_title(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        title=msg.text
    )

    await state.set_state(CreateCourseForm.get_description)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите описание курса',
        reply_markup=CANCEL_COURSE_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id,
    )


@router.message(StateFilter(CreateCourseForm.get_description))
async def get_course_description(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        description=msg.text
    )

    await state.set_state(CreateCourseForm.get_photo)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Отправьте фото курса',
        reply_markup=GET_COURSE_PHOTO_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id,
    )


@router.message(StateFilter(CreateCourseForm.get_photo), F.photo)
async def get_course_photo(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        file_manager: FromDishka[FileManager]
):
    user_id: int = msg.from_user.id
    photo_id: str = msg.photo[-1].file_id
    data: dict[str, Any] = await state.get_data()

    file_path = file_manager.generate_path(
        directories=(COURSES_DEFAULT_DIRECTORY,),
        filename=photo_id,
    )

    obj = await file_manager.get_by_file_path(file_path=file_path)
    if obj:
        return await msg.answer(
            text='Такое фото уже существует'
        )

    photo = await bot.download(file=photo_id)
    file_path = file_manager.generate_path(
        directories=(COURSES_DEFAULT_DIRECTORY,),
        filename=photo_id,
    )
    await file_manager.save(payload=photo.read(), file_path=file_path)

    await state.update_data(
        photo_id=photo_id,
        photo=None,
    )

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.set_state(state=CreateCourseForm.get_registrations_limit)

    msg = await bot.send_message(
        chat_id=user_id,
        text='И наконец, отправьте лимит на количество регистраций',
        reply_markup=GET_COURSE_REGISTRATIONS_LIMIT_KB
    )
    await state.update_data(
        msg_on_delete=msg.message_id,
    )


@router.callback_query(StateFilter(CreateCourseForm.get_photo), F.data == 'create_course-skip_photo')
async def skip_photo(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.update_data(
        photo_id=None,
        photo=None
    )

    await state.set_state(state=CreateCourseForm.get_registrations_limit)

    msg = await bot.send_message(
        chat_id=user_id,
        text='И наконец, отправьте лимит на количество регистраций',
        reply_markup=GET_COURSE_REGISTRATIONS_LIMIT_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateCourseForm.get_registrations_limit), F.text)
async def get_course_registrations_limit(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateCourseInteractor],
        user_role: UserRole,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.set_state(state=None)

    await interactor.execute(
        data=CreateCourseInputData(
            title=data['title'],
            description=data['description'],
            photo_id=data['photo_id'],
            photo=data['photo'],
            registrations_limit=msg.text
        )
    )

    del data['title']
    del data['description']
    del data['photo']
    del data['photo_id']

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    del data['msg_on_delete']
    await state.set_data(data)

    await bot.send_message(
        chat_id=user_id,
        text=f"Курс успешно создан. Вы вернулись в главное меню",
        reply_markup=get_main_menu_keyboard(user_role=user_role)
    )


@router.callback_query(StateFilter(CreateCourseForm.get_registrations_limit),
                       F.data == 'create_course-skip_registrations_limit')
async def skip_registrations_limit(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_role: UserRole,
        bot: Bot,
        interactor: FromDishka[CreateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.set_state(state=None)

    await interactor.execute(
        data=CreateCourseInputData(
            title=data['title'],
            description=data['description'],
            photo_id=data['photo_id'],
            photo=data['photo'],
            registrations_limit=None
        )
    )

    del data['title']
    del data['description']
    del data['msg_on_delete']
    del data['photo']
    del data['photo_id']
    await state.set_data(data)

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text=f"Курс успешно создан. Вы вернулись в главное меню",
        reply_markup=get_main_menu_keyboard(user_role=user_role)
    )


@router.callback_query(StateFilter(CreateCourseForm), F.data == 'create_course-cancel')
async def cancel_course_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        user_role: UserRole,
        file_manager: FromDishka[FileManager]
):
    user_id: int = callback_query.from_user.id
    data = await state.get_data()

    photo_id = data.get('photo_id', None)
    if photo_id:
        file_path = file_manager.generate_path(
            directories=(COURSES_DEFAULT_DIRECTORY,),
            filename=photo_id,
        )
        await file_manager.delete(file_path=file_path)

    await state.set_state(state=None)
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text=f"Создание курса отменено. Вы вернулись в главное меню",
        reply_markup=get_main_menu_keyboard(user_role=user_role),
    )
