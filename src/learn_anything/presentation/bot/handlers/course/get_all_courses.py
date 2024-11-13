import copy
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.application.input_data import Pagination
from learn_anything.application.interactors.course.get_many_courses import GetManyCoursesInteractor, \
    GetManyCoursesInputData, CoursePartialData
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import GetManyCoursesFilters, SortBy
from learn_anything.presentation.bot.keyboards.many_courses import get_all_courses_keyboard, get_all_courses_filters, \
    cancel_text_filter_input_kb
from learn_anything.presentation.bot.keyboards.main_menu import get_main_menu_keyboard
from learn_anything.presentation.bot.states.course import SearchAllBy

router = Router()

DEFAULT_LIMIT = 10
DEFAULT_FILTERS = lambda: GetManyCoursesFilters(sort_by=SortBy.POPULARITY)


@router.callback_query(F.data == 'main_menu-all_courses')
async def get_all_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetManyCoursesInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    output_data = await interactor.execute(
        GetManyCoursesInputData(
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
            filters=data.get('all_courses_filters', DEFAULT_FILTERS()),
        )
    )

    data = await state.update_data(
        all_courses=output_data.courses,
        all_courses_pointer=0,
        all_courses_offset=0,
        all_courses_total=output_data.total,
        all_courses_filters=data.get('all_courses_filters', DEFAULT_FILTERS()),
    )

    courses = output_data.courses
    total = output_data.total

    if total == 0:
        await bot.send_message(
            chat_id=user_id,
            text=f"No courses were found. Try to reset filters",
            reply_markup=get_all_courses_keyboard(
                pointer=0,
                total=total,
            )
        )
        return

    pointer = data['all_courses_pointer']
    current_course = courses[pointer]
    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Зарегестрировано: {current_course.total_registered}

Автор: {current_course.creator.title()}
Создан: {current_course.created_at}
""",
        reply_markup=get_all_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
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
        await state.set_state(SearchAllBy.author)
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=user_id, text='Введите имя автора', reply_markup=cancel_text_filter_input_kb())
        return

    if selected_option == 'title':
        await state.set_state(SearchAllBy.title)
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.send_message(
            chat_id=user_id,
            text='Введите название курса',
            reply_markup=cancel_text_filter_input_kb()
        )
        return

    if selected_option == 'popularones':
        selected_option = SortBy.POPULARITY
    else:
        selected_option = SortBy.DATE

    new_filters = data['all_courses_new_filters']
    new_filters.sort_by = selected_option

    await state.update_data(all_courses_new_filters=new_filters)

    await bot.edit_message_text(
        chat_id=user_id,
        text='Выберите фильтры',
        message_id=callback_query.message.message_id,
        reply_markup=get_all_courses_filters(
            current_filters=new_filters,
        ),
    )


@router.message(StateFilter(SearchAllBy.author))
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


@router.message(StateFilter(SearchAllBy.title))
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


@router.callback_query(StateFilter(SearchAllBy), F.data == 'all_courses_filters-cancel_input')
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
        all_courses_new_filters=DEFAULT_FILTERS(),
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
        interactor: FromDishka[GetManyCoursesInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

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
        all_courses_=courses,
        all_courses_total=total,
        all_courses_pointer=0,
        all_courses_offset=0,
    )

    if total == 0:
        await bot.send_message(
            chat_id=user_id,
            text=f"No courses were found. Try to reset filters",
            reply_markup=get_all_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course = courses[data['all_courses_pointer']]
    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Зарегестрировано: {current_course.total_registered}

Автор: {current_course.creator.title()}

Создан: {current_course.created_at}
    """,
        reply_markup=get_all_courses_keyboard(
            pointer=0,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'all_courses_filters-back')
async def filters_back(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    await state.update_data(
        all_courses_new_filters=None,
    )

    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    courses = data['all_courses']
    total = data['all_courses_total']
    pointer = data['all_courses_pointer']

    if total == 0:
        await bot.send_message(
            chat_id=user_id,
            text=f"No courses were found. Try to reset filters",
            reply_markup=get_all_courses_keyboard(
                pointer=0,
                total=0,
            )
        )
        return

    current_course = courses[pointer]
    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Автор: {current_course.creator.title()}

Зарегестрировано: {current_course.total_registered}

Создан: {current_course.created_at}
    """,
        reply_markup=get_all_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'all_courses-to_main_menu')
async def to_main_menu(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        id_provider: FromDishka[IdentityProvider],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    role = data.get('role')
    if not role:
        role = await id_provider.get_role()
        data['role'] = role

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text='Вы вернулись в главное меню',
        reply_markup=get_main_menu_keyboard(user_role=role),
    )


@router.callback_query(F.data.in_(['all_courses-next', 'all_courses-prev']))
async def watch_all_courses_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetManyCoursesInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    command = callback_query.data.split('-')[1]

    pointer = data['all_courses_pointer']
    courses: list[CoursePartialData] = data['all_courses']
    offset: int = data['all_courses_offset']
    total = data['all_courses_total']

    if command == 'next':
        if (pointer + 1) % DEFAULT_LIMIT == 0:
            output_data = await interactor.execute(
                GetManyCoursesInputData(
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                    filters=data.get('all_courses_filters', DEFAULT_FILTERS()),
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

    current_course = courses[pointer]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Зарегестрировано: {current_course.total_registered}

Создан: {current_course.created_at}
""",
        reply_markup=get_all_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )
