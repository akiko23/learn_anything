import copy
from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from dishka import FromDishka

from learn_anything.course_platform.application.input_data import Pagination
from learn_anything.course_platform.application.interactors.course.get_many_courses import \
    GetActorRegisteredCoursesInteractor, \
    GetManyCoursesInputData, CourseData
from learn_anything.course_platform.application.interactors.course.update_course import UpdateCourseInputData, \
    UpdateCourseInteractor
from learn_anything.course_platform.application.ports.data.course_gateway import GetManyCoursesFilters, SortBy
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException
from learn_anything.course_platform.presentation.tg_bot.states.course import SearchRegisteredByForm
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.many_courses import cancel_text_filter_input_kb
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.many_courses import \
    get_actor_registered_courses_keyboard, \
    get_actor_registered_courses_filters_kb
from learn_anything.course_platform.presentors.tg_bot.texts.get_many_courses import get_many_courses_text

router = Router()

DEFAULT_LIMIT = 50
DEFAULT_FILTERS = GetManyCoursesFilters(sort_by=SortBy.POPULARITY)


@router.callback_query(
    F.data == 'main_menu-get_registered_courses',
    F.message.as_('callback_query_message')
)
async def get_actor_registered_courses(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorRegisteredCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
        file_manager: FromDishka[FileManager],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    offset = data.get('registered_courses_offset', 0)
    pointer = data.get('registered_courses_pointer', 0)
    filters = data.get('registered_courses_filters', DEFAULT_FILTERS)

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=offset, limit=DEFAULT_LIMIT),
            filters=filters,
        )
    )

    courses = data.get('registered_courses', output_data.courses)
    courses[offset: offset + DEFAULT_LIMIT] = output_data.courses

    total = output_data.total

    await state.update_data(
        registered_courses=courses,
        registered_courses_pointer=pointer,
        registered_courses_offset=offset,
        registered_courses_total=output_data.total,
        registered_courses_filters=filters,
    )

    if total == 0:
        msg_text = 'Вы не зарегестрированы ни на один курс'
        if filters != DEFAULT_FILTERS:
            msg_text = "Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            text=msg_text,
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=0,
                hide_filters=(filters == DEFAULT_FILTERS)
            )
        )
        return

    current_course = courses[pointer]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_actor_registered_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='registered_courses',
        )


@router.callback_query(
    F.data == 'actor_registered_courses-filters',
    F.message.as_('callback_query_message')
)
async def get_filters(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        registered_courses_new_filters=copy.copy(data['registered_courses_filters']),
    )

    current_filters = data['registered_courses_filters']
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query_message.message_id,
        reply_markup=get_actor_registered_courses_filters_kb(current_filters),
    )


@router.callback_query(
    F.data == 'actor_registered_courses_filters-title',
    F.message.as_('callback_query_message')
)
async def proces_actor_registered_courses_filters(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id

    await state.set_state(SearchRegisteredByForm.title)

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите название курса',
        reply_markup=cancel_text_filter_input_kb(back_to='registered_courses')
    )
    await state.update_data(msg_for_delete=msg.message_id + 1)


@router.message(
    StateFilter(SearchRegisteredByForm.title),
    F.text.as_('title')
)
async def process_actor_registered_courses_title_filter(
        msg: Message,
        title: str,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    new_filters = data['registered_courses_new_filters']
    new_filters.title = title

    await state.set_state(state=None)
    await state.update_data(registered_courses_new_filters=new_filters)

    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_actor_registered_courses_filters_kb(
            current_filters=new_filters,
        ),
    )


@router.callback_query(
    StateFilter(SearchRegisteredByForm), F.data == 'registered_courses_filters-cancel_input',
    F.message.as_('callback_query_message')
)
async def cancel_registered_courses_input_filters(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.set_state(state=None)

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_actor_registered_courses_filters_kb(
            current_filters=data['registered_courses_new_filters'],
        ),
    )


@router.callback_query(
    F.data == 'actor_registered_courses_filters-reset',
    F.message.as_('callback_query_message')
)
async def reset_course_actor_registered_filters(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id

    data = await state.update_data(
        registered_courses_new_filters=DEFAULT_FILTERS,
        registered_courses_pointer=0,
        registered_courses_offset=0,
    )

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query_message.message_id,
        reply_markup=get_actor_registered_courses_filters_kb(
            current_filters=data['registered_courses_new_filters']
        )
    )


@router.callback_query(
    F.data == 'actor_registered_courses_filters-apply',
    F.message.as_('callback_query_message')
)
async def apply_courses_actor_registered_filters(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorRegisteredCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
        file_manager: FromDishka[FileManager],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    data = await state.update_data(
        registered_courses_filters=data['registered_courses_new_filters'],
        registered_courses_new_filters=None,
    )

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
            filters=data['registered_courses_filters'],
        )
    )

    courses = output_data.courses
    total = output_data.total

    data = await state.update_data(
        registered_courses=courses,
        registered_courses_total=total,
        registered_courses_pointer=0,
        registered_courses_offset=0,
    )

    filters = data['registered_courses_filters']

    if total == 0:
        msg_text = 'Вы не зарегестрированы ни на один курс'
        if filters != DEFAULT_FILTERS:
            msg_text = "Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            text=msg_text,
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=0,
                hide_filters=(filters == DEFAULT_FILTERS)
            )
        )
        return

    current_course = courses[data['registered_courses_pointer']]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_actor_registered_courses_keyboard(
                pointer=0,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='registered_courses',
        )


@router.callback_query(
    F.data == 'actor_registered_courses_filters-back',
    F.message.as_('callback_query_message')
)
async def actor_registered_courses_filters_back(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        update_course_interactor: FromDishka[UpdateCourseInteractor],
        file_manager: FromDishka[FileManager],
) -> None:
    await state.update_data(
        registered_courses_new_filters=None,
    )

    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    filters = data['registered_courses_filters']

    courses = data['registered_courses']
    total = data['registered_courses_total']
    pointer = data['registered_courses_pointer']

    if total == 0:
        msg_text = 'Вы не зарегестрированы ни на один курс'
        if filters != DEFAULT_FILTERS:
            msg_text = "Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            text=msg_text,
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=0,
                hide_filters=(filters == DEFAULT_FILTERS)
            )
        )
        return

    current_course: CourseData = courses[pointer]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id and current_course.photo_path:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_actor_registered_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='registered_courses',
        )


@router.callback_query(
    F.data.in_(['actor_registered_courses-next', 'actor_registered_courses-prev']),
    F.data.as_('callback_query_data'),
    F.message.as_('callback_query_message')
)
async def watch_actor_registered_courses_prev_or_next(
        callback_query: CallbackQuery,
        callback_query_data: str,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorRegisteredCoursesInteractor],
        file_manager: FromDishka[FileManager],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()
    command = callback_query_data.split('-')[1]

    pointer = data['registered_courses_pointer']
    courses: list[CourseData] = data['registered_courses']
    offset: int = data['registered_courses_offset']
    total = data['registered_courses_total']

    if command == 'next':
        if (pointer + 1) == (offset + DEFAULT_LIMIT):
            output_data = await interactor.execute(
                GetManyCoursesInputData(
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                    filters=data.get('registered_courses_filters', DEFAULT_FILTERS),
                )
            )

            courses.extend(output_data.courses)
            await state.update_data(
                registered_courses=courses,
                registered_courses_offset=offset + DEFAULT_LIMIT,
                registered_courses_total=output_data.total
            )

        pointer += 1
    else:
        pointer -= 1

    await state.update_data(
        registered_courses_pointer=pointer,
    )

    current_course = courses[pointer]
    text = get_many_courses_text(current_course)

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if current_course.photo_id:
        photo_id = current_course.photo_id
        photo_path = current_course.photo_path

    try:
        await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=get_actor_registered_courses_keyboard(
                pointer=pointer,
                total=total,
                current_course_id=current_course.id,
            ),
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=current_course.id
            ),
            collection_key='registered_courses',
        )
