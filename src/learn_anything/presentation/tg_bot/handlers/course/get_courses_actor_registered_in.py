import copy
from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from dishka import FromDishka

from learn_anything.application.input_data import Pagination
from learn_anything.application.interactors.course.get_many_courses import GetActorRegisteredCoursesInteractor, \
    GetManyCoursesInputData, CourseData
from learn_anything.application.interactors.course.update_course import UpdateCourseInputData, UpdateCourseInteractor
from learn_anything.application.ports.data.course_gateway import GetManyCoursesFilters, SortBy
from learn_anything.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException
from learn_anything.presentation.tg_bot.states.course import SearchRegisteredByForm
from learn_anything.presentors.tg_bot.keyboards.course.many_courses import cancel_text_filter_input_kb
from learn_anything.presentors.tg_bot.keyboards.course.many_courses import get_actor_registered_courses_keyboard, \
    get_actor_registered_courses_filters_kb
from learn_anything.presentors.tg_bot.texts.get_many_courses import get_many_courses_text

router = Router()

DEFAULT_LIMIT = 50
DEFAULT_FILTERS = GetManyCoursesFilters(sort_by=SortBy.POPULARITY)


@router.callback_query(F.data == 'main_menu-get_registered_courses')
async def get_actor_registered_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorRegisteredCoursesInteractor],
        update_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
            filters=data.get('registered_courses_filters', DEFAULT_FILTERS),
        )
    )

    current_filters = data.get('registered_courses_filters', DEFAULT_FILTERS)

    data = await state.update_data(
        registered_courses=output_data.courses,
        registered_courses_pointer=0,
        registered_courses_offset=0,
        registered_courses_total=output_data.total,
        registered_courses_filters=current_filters,
    )

    courses = output_data.courses
    total = output_data.total

    if total == 0:
        msg_text = 'Вы не зарегестрированы ни на один курс'
        if current_filters != DEFAULT_FILTERS:
            msg_text = f"Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=total,
            )
        )
        return

    pointer = data['registered_courses_pointer']
    current_course = courses[pointer]
    text = get_many_courses_text(current_course)

    if current_course.photo_id:
        try:
            return await bot.send_photo(
                chat_id=user_id,
                photo=current_course.photo_id,
                caption=text,
                reply_markup=get_actor_registered_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )
        except TelegramBadRequest:
            raise NoMediaOnTelegramServersException(
                media_buffer=current_course.photo_reader,
                text_to_send=text,
                keyboard=get_actor_registered_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
                update_interactor=update_interactor,
                interactor_input_data=UpdateCourseInputData(
                    course_id=current_course.id
                )
            )

    await bot.send_message(
        chat_id=user_id,
        text=get_many_courses_text(current_course),
        reply_markup=get_actor_registered_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'actor_registered_courses-filters')
async def get_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        registered_courses_new_filters=copy.copy(data['registered_courses_filters']),
    )

    current_filters = data['registered_courses_filters']
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_actor_registered_courses_filters_kb(current_filters),
    )


@router.callback_query(F.data == 'actor_registered_courses_filters-title')
async def proces_actor_registered_courses_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id

    await state.update_data(msg_for_delete=callback_query.message.message_id + 1)

    await state.set_state(SearchRegisteredByForm.title)
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text='Введите название курса',
        reply_markup=cancel_text_filter_input_kb()
    )


@router.message(StateFilter(SearchRegisteredByForm.title))
async def process_actor_registered_courses_title_filter(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    await state.set_state(state=None)

    title: str = msg.text
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    new_filters = data['registered_courses_new_filters']
    new_filters.title = title
    await state.update_data(registered_courses_new_filters=new_filters)

    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_actor_registered_courses_filters_kb(
            current_filters=new_filters,
        ),
    )


@router.callback_query(StateFilter(SearchRegisteredByForm), F.data == 'actor_registered_courses_filters-cancel_input')
async def cancel_registered_courses_title_input_filter(
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
        reply_markup=get_actor_registered_courses_filters_kb(
            current_filters=data['registered_courses_new_filters'],
        ),
    )


@router.callback_query(F.data == 'actor_registered_courses_filters-reset')
async def reset_course_actor_registered_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id

    data = await state.update_data(
        registered_courses_new_filters=DEFAULT_FILTERS,
        registered_courses_pointer=0,
        registered_courses_offset=0,
    )

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_actor_registered_courses_filters_kb(
            current_filters=data['registered_courses_new_filters']
        )
    )


@router.callback_query(F.data == 'actor_registered_courses_filters-apply')
async def apply_courses_actor_registered_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorRegisteredCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],

):
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
            msg_text = f"Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=msg_text,
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course = courses[data['registered_courses_pointer']]
    text = get_many_courses_text(current_course)

    if current_course.photo_id:
        try:
            return await bot.edit_message_media(
                chat_id=user_id,
                message_id=callback_query.message.message_id,
                media=InputMediaPhoto(
                    media=current_course.photo_id,
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
                media_buffer=current_course.photo_reader,
                text_to_send=text,
                keyboard=get_actor_registered_courses_keyboard(
                    pointer=0,
                    total=total,
                    current_course_id=current_course.id,
                ),
                update_interactor=update_course_interactor,
                interactor_input_data=UpdateCourseInputData(
                    course_id=current_course.id
                )
            )

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=get_many_courses_text(current_course),
        reply_markup=get_actor_registered_courses_keyboard(
            pointer=0,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'actor_registered_courses_filters-back')
async def actor_registered_courses_filters_back(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
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
            msg_text = f"Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=msg_text,
            reply_markup=get_actor_registered_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course: CourseData = courses[pointer]
    text = get_many_courses_text(current_course)

    if current_course.photo_id:
        try:
            return await bot.edit_message_media(
                chat_id=user_id,
                message_id=callback_query.message.message_id,
                media=InputMediaPhoto(
                    media=current_course.photo_id,
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
                media_buffer=current_course.photo_reader,
                text_to_send=text,
                keyboard=get_actor_registered_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
                update_interactor=update_course_interactor,
                interactor_input_data=UpdateCourseInputData(
                    course_id=current_course.id
                )
            )

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=get_actor_registered_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data.in_(['actor_registered_courses-next', 'actor_registered_courses-prev']))
async def watch_actor_registered_courses_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorRegisteredCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    command = callback_query.data.split('-')[1]

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

    if current_course.photo_id:
        try:
            return await bot.send_photo(
                chat_id=user_id,
                photo=current_course.photo_id,
                caption=text,
                reply_markup=get_actor_registered_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )
        except TelegramBadRequest:
            raise NoMediaOnTelegramServersException(
                media_buffer=current_course.photo_reader,
                text_to_send=text,
                keyboard=get_actor_registered_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
                update_interactor=update_course_interactor,
                interactor_input_data=UpdateCourseInputData(
                    course_id=current_course.id
                )
            )

    await bot.send_message(
        chat_id=user_id,
        text=get_many_courses_text(current_course),
        reply_markup=get_actor_registered_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )
