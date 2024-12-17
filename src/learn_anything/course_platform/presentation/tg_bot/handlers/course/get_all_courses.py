import copy
from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaPhoto
from dishka import FromDishka

from learn_anything.course_platform.application.input_data import Pagination
from learn_anything.course_platform.application.interactors.course.get_many_courses import GetAllCoursesInteractor, \
    GetManyCoursesInputData, CourseData
from learn_anything.course_platform.application.interactors.course.update_course import UpdateCourseInteractor, UpdateCourseInputData
from learn_anything.course_platform.application.ports.data.course_gateway import GetManyCoursesFilters, SortBy
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.domain.entities.user.models import UserRole
from learn_anything.course_platform.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException
from learn_anything.course_platform.presentation.tg_bot.states.course import SearchAllByForm
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.many_courses import get_all_courses_keyboard, \
    get_all_courses_filters, \
    cancel_text_filter_input_kb
from learn_anything.course_platform.presentors.tg_bot.keyboards.main_menu import get_main_menu_keyboard
from learn_anything.course_platform.presentors.tg_bot.texts.get_many_courses import get_many_courses_text

router = Router()

DEFAULT_LIMIT = 10
DEFAULT_FILTERS = GetManyCoursesFilters(sort_by=SortBy.POPULARITY)


@router.callback_query(F.data == 'main_menu-all_courses')
async def get_all_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetAllCoursesInteractor],
        file_manager: FromDishka[FileManager],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    filters = data.get('all_courses_filters', DEFAULT_FILTERS)
    pointer = data.get('all_courses_pointer', 0)
    offset = data.get('all_courses_offset', 0)

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=offset, limit=DEFAULT_LIMIT),
            filters=filters,
        )
    )
    courses = data.get('all_courses', output_data.courses)
    courses[offset: offset + DEFAULT_LIMIT] = output_data.courses

    total = output_data.total

    await state.update_data(
        all_courses=courses,
        all_courses_pointer=pointer,
        all_courses_offset=offset,
        all_courses_total=output_data.total,
        all_courses_filters=filters,
    )


    if total == 0:
        msg_text = 'Еще ни один курс не был опубликован :('
        if filters != DEFAULT_FILTERS:
            msg_text = "Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_all_courses_keyboard(
                pointer=0,
                total=total,
            )
        )
        return

    current_course: CourseData = courses[pointer]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        return await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='all_courses',
        )


@router.callback_query(F.data == 'all_courses-filters')
async def get_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        all_courses_new_filters=copy.copy(data['all_courses_filters']),
    )

    current_filters = data['all_courses_filters']
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_all_courses_filters(current_filters),
    )


@router.callback_query(F.data.in_([
    'all_courses_filters-popularones',
    'all_courses_filters-newones',
    'all_courses_filters-author',
    'all_courses_filters-title',
]))
async def sort_by_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    selected_option = callback_query.data.split('-')[1]
    if selected_option == 'author':
        await state.set_state(SearchAllByForm.author)
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.send_message(
            chat_id=user_id,
            text='Введите имя автора',
            reply_markup=cancel_text_filter_input_kb(back_to='all_courses')
        )
        return

    if selected_option == 'title':
        await state.set_state(SearchAllByForm.title)
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.send_message(
            chat_id=user_id,
            text='Введите название курса',
            reply_markup=cancel_text_filter_input_kb(back_to='all_courses')
        )
        return

    if selected_option == 'popularones':
        selected_option = SortBy.POPULARITY
    else:
        selected_option = SortBy.DATE

    new_filters = data['all_courses_new_filters']
    new_filters.sort_by = selected_option

    await state.update_data(all_courses_new_filters=new_filters)

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_all_courses_filters(
            current_filters=new_filters,
        ),
    )


@router.message(StateFilter(SearchAllByForm.author))
async def process_author_filter(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    await state.set_state(state=None)

    author: str = msg.text
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    new_filters = data['all_courses_new_filters']
    new_filters.author_name = author
    await state.update_data(all_courses_new_filters=new_filters)

    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_all_courses_filters(
            current_filters=new_filters,
        ),
    )


@router.message(StateFilter(SearchAllByForm.title))
async def process_title_filter(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    await state.set_state(state=None)

    title: str = msg.text
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    new_filters = data['all_courses_new_filters']
    new_filters.title = title
    await state.update_data(all_courses_new_filters=new_filters)

    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_all_courses_filters(
            current_filters=new_filters,
        ),
    )


@router.callback_query(StateFilter(SearchAllByForm), F.data == 'all_courses_filters-cancel_input')
async def cancel_text_input_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await state.set_state(state=None)
    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_all_courses_filters(
            current_filters=data['all_courses_new_filters'],
        ),
    )


@router.callback_query(F.data == 'all_courses_filters-reset')
async def reset_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id

    data = await state.update_data(
        all_courses_new_filters=DEFAULT_FILTERS,
        all_courses_pointer=0,
        all_courses_offset=0,
    )

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_all_courses_filters(
            current_filters=data['all_courses_new_filters']
        )
    )


@router.callback_query(F.data == 'all_courses_filters-apply')
async def apply_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetAllCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
        file_manager: FromDishka[FileManager]
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    data = await state.update_data(
        all_courses_filters=data['all_courses_new_filters'],
        all_courses_new_filters=None,
    )

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
            filters=data['all_courses_filters'],
        )
    )

    courses = output_data.courses
    total = output_data.total

    data = await state.update_data(
        all_courses=courses,
        all_courses_total=total,
        all_courses_pointer=0,
        all_courses_offset=0,
    )

    filters = data['all_courses_filters']

    if total == 0:
        msg_text = 'Еще ни один курс не был опубликован :('
        if filters != DEFAULT_FILTERS:
            msg_text = "Ни одного курса не найдено. Попробуйте сбросить фильтры"

        return await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_all_courses_keyboard(
                pointer=0,
                total=0,
            )
        )

    current_course: CourseData = courses[data['all_courses_pointer']]
    text = get_many_courses_text(current_course)
    pointer = 0

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        return await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='all_courses',
        )


@router.callback_query(F.data == 'all_courses_filters-back')
async def filters_back(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        file_manager: FromDishka[FileManager],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    await state.update_data(
        all_courses_new_filters=None,
    )

    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    filters = data['all_courses_filters']

    courses = data['all_courses']
    total = data['all_courses_total']
    pointer = data['all_courses_pointer']

    if total == 0:
        msg_text = 'Eще ни один курс не был опубликован :('
        if filters != DEFAULT_FILTERS:
            msg_text = "Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.edit_message_text(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_all_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course: CourseData = courses[pointer]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        return await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='all_courses',
        )


@router.callback_query(F.data.in_(['all_courses-next', 'all_courses-prev']))
async def watch_all_courses_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetAllCoursesInteractor],
        file_manager: FromDishka[FileManager],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    command = callback_query.data.split('-')[1]

    pointer = data['all_courses_pointer']
    courses: list[CourseData] = data['all_courses']
    offset: int = data['all_courses_offset']
    total = data['all_courses_total']

    if command == 'next':
        if (pointer + 1) == (offset + DEFAULT_LIMIT):
            output_data = await interactor.execute(
                GetManyCoursesInputData(
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                    filters=data.get('all_courses_filters', DEFAULT_FILTERS),
                )
            )

            courses.extend(output_data.courses)
            await state.update_data(
                all_courses=courses,
                all_courses_offset=offset + DEFAULT_LIMIT,
                all_courses_total=output_data.total
            )

        pointer += 1

    else:
        pointer -= 1

    await state.update_data(
        all_courses_pointer=pointer,
    )

    current_course: CourseData = courses[pointer]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        return await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_all_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='all_courses',
        )


@router.callback_query(F.data == 'all_courses-to_main_menu')
async def to_main_menu(
        callback_query: CallbackQuery,
        bot: Bot,
        user_role: UserRole,
):
    user_id: int = callback_query.from_user.id

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text='Вы вернулись в главное меню',
        reply_markup=get_main_menu_keyboard(user_role=user_role),
    )
