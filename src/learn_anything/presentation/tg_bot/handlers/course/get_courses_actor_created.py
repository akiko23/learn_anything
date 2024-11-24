import copy
from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.application.input_data import Pagination
from learn_anything.application.interactors.course.get_many_courses import GetManyCoursesInteractor, \
    GetManyCoursesInputData, CourseData
from learn_anything.application.interactors.course.update_course import UpdateCourseInteractor, UpdateCourseInputData
from learn_anything.application.ports.data.course_gateway import GetManyCoursesFilters, SortBy
from learn_anything.entities.course.models import CourseID
from learn_anything.presentation.tg_bot.handlers.course.get_all_courses import get_course_text
from learn_anything.presentation.tg_bot.keyboards.course.many_courses import cancel_text_filter_input_kb, \
    get_actor_created_courses_keyboard, get_actor_created_courses_filters_kb
from learn_anything.presentation.tg_bot.states.course import SearchCreatedBy

router = Router()

DEFAULT_LIMIT = 10
DEFAULT_FILTERS = lambda actor_id: GetManyCoursesFilters(sort_by=SortBy.DATE, with_creator_id=actor_id)


@router.callback_query(F.data == 'main_menu-get_created_courses')
async def get_actor_created_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetManyCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    filters = data.get('created_courses_filters', DEFAULT_FILTERS(actor_id=user_id))

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
            filters=filters,
        )
    )

    data = await state.update_data(
        created_courses=output_data.courses,
        created_courses_pointer=0,
        created_courses_offset=0,
        created_courses_total=output_data.total,
        created_courses_filters=filters,
    )

    courses = output_data.courses
    total = output_data.total

    if total == 0:
        msg_text = 'Вы еще не создали ни одного курса'
        if filters != DEFAULT_FILTERS(actor_id=user_id):
            msg_text = f"Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_actor_created_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    pointer = data['created_courses_pointer']
    current_course = courses[pointer]
    text = get_course_text(current_course, write_registered=True)

    if current_course.photo_id:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=current_course.photo_id,
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )
        except TelegramBadRequest:
            msg = await bot.send_photo(
                chat_id=user_id,
                photo=BufferedInputFile(current_course.photo_reader.read(), 'stub'),
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )

            new_photo_id = msg.photo[-1].file_id
            new_photo = await bot.download(new_photo_id)

            await update_course_interactor.execute(
                data=UpdateCourseInputData(
                    course_id=CourseID(int(current_course.id)),
                    photo_id=new_photo_id,
                    photo=new_photo
                )
            )
        return

    await bot.send_message(
        chat_id=user_id,
        text=get_course_text(current_course, write_registered=True),
        reply_markup=get_actor_created_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'actor_created_courses-filters')
async def get_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        created_courses_new_filters=copy.copy(data['created_courses_filters']),
    )

    current_filters = data['created_courses_filters']
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_actor_created_courses_filters_kb(current_filters),
    )


@router.callback_query(F.data == 'actor_created_courses_filters-title')
async def proces_actor_created_courses_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id

    await state.update_data(msg_for_delete=callback_query.message.message_id + 1)

    await state.set_state(SearchCreatedBy.title)
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text='Введите название курса',
        reply_markup=cancel_text_filter_input_kb()
    )


@router.message(StateFilter(SearchCreatedBy.title))
async def process_actor_created_courses_title_filter(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    await state.set_state(state=None)

    title: str = msg.text
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    new_filters = data['created_courses_new_filters']
    new_filters.title = title
    await state.update_data(created_courses_new_filters=new_filters)

    await bot.send_message(
        chat_id=user_id,
        text='Выберите фильтры',
        reply_markup=get_actor_created_courses_filters_kb(
            current_filters=new_filters,
        ),
    )


@router.callback_query(StateFilter(SearchCreatedBy), F.data == 'actor_created_courses_filters-cancel_input')
async def cancel_title_input_filter(
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
        reply_markup=get_actor_created_courses_filters_kb(
            current_filters=data['created_courses_new_filters'],
        ),
    )


@router.callback_query(F.data == 'actor_created_courses_filters-reset')
async def reset_course_actor_created_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id

    data = await state.update_data(
        created_courses_new_filters=DEFAULT_FILTERS(actor_id=user_id),
        created_courses_pointer=0,
        created_courses_offset=0,
    )

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_actor_created_courses_filters_kb(
            current_filters=data['created_courses_new_filters']
        )
    )


@router.callback_query(F.data == 'actor_created_courses_filters-apply')
async def apply_courses_actor_created_filters(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetManyCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    data = await state.update_data(
        created_courses_filters=data['created_courses_new_filters'],
        created_courses_new_filters=None,
    )

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
            filters=data['created_courses_filters'],
        )
    )

    courses = output_data.courses
    total = output_data.total

    data = await state.update_data(
        created_courses=courses,
        created_courses_total=total,
        created_courses_pointer=0,
        created_courses_offset=0,
    )

    filters = data['created_courses_filters']

    if total == 0:
        msg_text = 'Вы еще не создали ни одного курса'
        if filters != DEFAULT_FILTERS(actor_id=user_id):
            msg_text = f"Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_actor_created_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course = courses[data['created_courses_pointer']]
    text = get_course_text(current_course, write_registered=True)

    if current_course.photo_id:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=current_course.photo_id,
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=0,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )
        except TelegramBadRequest:
            msg = await bot.send_photo(
                chat_id=user_id,
                photo=BufferedInputFile(current_course.photo_reader.read(), 'stub'),
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=0,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )

            new_photo_id = msg.photo[-1].file_id
            new_photo = await bot.download(new_photo_id)

            await update_course_interactor.execute(
                data=UpdateCourseInputData(
                    course_id=CourseID(int(current_course.id)),
                    photo_id=new_photo_id,
                    photo=new_photo
                )
            )
        return

    await bot.send_message(
        chat_id=user_id,
        text=get_course_text(current_course, write_registered=True),
        reply_markup=get_actor_created_courses_keyboard(
            pointer=0,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'actor_created_courses_filters-back')
async def actor_created_courses_filters_back(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        update_course_interactor: FromDishka[UpdateCourseInteractor],

):
    await state.update_data(
        created_courses_new_filters=None,
    )

    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    filters = data['created_courses_filters']

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    courses = data['created_courses']
    total = data['created_courses_total']
    pointer = data['created_courses_pointer']

    if total == 0:
        msg_text = 'Вы еще не создали ни одного курса'
        if filters != DEFAULT_FILTERS(actor_id=user_id):
            msg_text = f"Ни одного курса не найдено. Попробуйте сбросить фильтры"

        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_actor_created_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course = courses[pointer]
    text = get_course_text(current_course, write_registered=True)

    if current_course.photo_id:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=current_course.photo_id,
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )
        except TelegramBadRequest:
            msg = await bot.send_photo(
                chat_id=user_id,
                photo=BufferedInputFile(current_course.photo_reader.read(), 'stub'),
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )

            new_photo_id = msg.photo[-1].file_id
            new_photo = await bot.download(new_photo_id)

            await update_course_interactor.execute(
                data=UpdateCourseInputData(
                    course_id=CourseID(int(current_course.id)),
                    photo_id=new_photo_id,
                    photo=new_photo
                )
            )
        return

    await bot.send_message(
        chat_id=user_id,
        text=get_course_text(current_course, write_registered=True),
        reply_markup=get_actor_created_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data.in_(['actor_created_courses-next', 'actor_created_courses-prev']))
async def watch_actor_created_courses_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetManyCoursesInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    command = callback_query.data.split('-')[1]

    pointer = data['created_courses_pointer']
    courses: list[CourseData] = data['created_courses']
    offset: int = data['created_courses_offset']
    total = data['created_courses_total']

    if command == 'next':
        if (pointer + 1) % DEFAULT_LIMIT == 0:
            output_data = await interactor.execute(
                GetManyCoursesInputData(
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                    filters=data.get('created_courses_filters', DEFAULT_FILTERS(actor_id=user_id)),
                )
            )

            courses.extend(output_data.courses)
            await state.update_data(
                created_courses=courses,
                created_courses_offset=offset + DEFAULT_LIMIT,
                created_courses_total=output_data.total
            )

        pointer += 1

    else:
        pointer -= 1

    await state.update_data(
        created_courses_pointer=pointer,
    )

    current_course = courses[pointer]
    text = get_course_text(current_course, write_registered=True)

    if current_course.photo_id:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=current_course.photo_id,
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )
        except TelegramBadRequest:
            msg = await bot.send_photo(
                chat_id=user_id,
                photo=BufferedInputFile(current_course.photo_reader.read(), 'stub'),
                caption=text,
                reply_markup=get_actor_created_courses_keyboard(
                    pointer=pointer,
                    total=total,
                    current_course_id=current_course.id,
                ),
            )

            new_photo_id = msg.photo[-1].file_id
            new_photo = await bot.download(new_photo_id)

            await update_course_interactor.execute(
                data=UpdateCourseInputData(
                    course_id=CourseID(int(current_course.id)),
                    photo_id=new_photo_id,
                    photo=new_photo
                )
            )
        return

    await bot.send_message(
        chat_id=user_id,
        text=get_course_text(current_course, write_registered=True),
        reply_markup=get_actor_created_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )
