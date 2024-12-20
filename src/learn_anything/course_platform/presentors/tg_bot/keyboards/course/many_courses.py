from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.course_platform.application.ports.data.course_gateway import GetManyCoursesFilters, SortBy
from learn_anything.course_platform.domain.entities.course.models import CourseID


def get_all_courses_keyboard(pointer: int, total: int, current_course_id: CourseID | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Фильтры', callback_data='all_courses-filters')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='all_courses-prev'),
            InlineKeyboardButton(text='➡️', callback_data='all_courses-next'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data='all_courses-next'),
        ])

    if (pointer + 1) == total and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='all_courses-prev'),
        ])

    if current_course_id:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='Перейти к курсу', callback_data=f'course-all_courses-{current_course_id}'),
        ])

    return kb


def get_all_courses_filters(current_filters: GetManyCoursesFilters) -> InlineKeyboardMarkup:
    default_filters = GetManyCoursesFilters(sort_by=SortBy.POPULARITY)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Искать по автору', callback_data='all_courses_filters-author')],
            [InlineKeyboardButton(text='Искать по названию', callback_data='all_courses_filters-title')],
            [
                InlineKeyboardButton(text='Сначала популярные ✔️', callback_data='all_courses_filters-popularones'),
                InlineKeyboardButton(text='Сначала новые', callback_data='all_courses_filters-newones'),
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data='all_courses_filters-back'),
                InlineKeyboardButton(text='Применить', callback_data='all_courses_filters-apply'),
            ]
        ]
    )

    if current_filters.author_name:
        kb.inline_keyboard[0] = [
            InlineKeyboardButton(
                text=f'Искать по автору (Текущий: {current_filters.author_name})',
                callback_data='all_courses_filters-author',
            ),
        ]

    if current_filters.title:
        kb.inline_keyboard[1] = [
            InlineKeyboardButton(
                text=f'Искать по названию (Текущее: {current_filters.title})',
                callback_data='all_courses_filters-title',
            ),
        ]

    if current_filters.sort_by == SortBy.DATE:
        kb.inline_keyboard[2] = [
            InlineKeyboardButton(text='Сначала популярные', callback_data='all_courses_filters-popularones'),
            InlineKeyboardButton(text='Сначала новые ✔️', callback_data='all_courses_filters-newones'),
        ]

    if current_filters != default_filters:
        kb.inline_keyboard.insert(
            0, [InlineKeyboardButton(text='Сбросить', callback_data='all_courses_filters-reset')],
        )

    return kb


def cancel_text_filter_input_kb(back_to: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data=f'{back_to}_filters-cancel_input')]
        ]
    )


def get_actor_created_courses_keyboard(pointer: int, total: int, current_course_id: CourseID | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Фильтры', callback_data='actor_created_courses-filters')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='actor_created_courses-prev'),
            InlineKeyboardButton(text='➡️', callback_data='actor_created_courses-next'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data='actor_created_courses-next'),
        ])

    if (pointer + 1 == total) and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='actor_created_courses-prev'),
        ])

    if current_course_id:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='Перейти к курсу', callback_data=f'course-created_courses-{current_course_id}'),
        ])

    return kb


def get_actor_created_courses_filters_kb(current_filters: GetManyCoursesFilters) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Искать по названию', callback_data='actor_created_courses_filters-title')],
            [
                InlineKeyboardButton(text='Назад', callback_data='actor_created_courses_filters-back'),
                InlineKeyboardButton(text='Применить', callback_data='actor_created_courses_filters-apply'),
            ]
        ]
    )

    if current_filters.title:
        kb.inline_keyboard[0] = [
            InlineKeyboardButton(
                text=f'Искать по названию (Текущее: {current_filters.title})',
                callback_data='actor_created_courses_filters-title',
            ),
        ]
        kb.inline_keyboard.insert(
            1, [InlineKeyboardButton(text='Сбросить', callback_data='actor_created_courses_filters-reset')],
        )

    return kb


def get_actor_registered_courses_keyboard(pointer: int, total: int, current_course_id: CourseID | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Фильтры', callback_data='actor_registered_courses-filters')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='actor_registered_courses-prev'),
            InlineKeyboardButton(text='➡️', callback_data='actor_registered_courses-next'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data='actor_registered_courses-next'),
        ])

    if (pointer + 1 == total) and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='actor_registered_courses-prev'),
        ])

    if current_course_id:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='Перейти к курсу',
                                 callback_data=f'course-registered_courses-{current_course_id}'),
        ])

    return kb


def get_actor_registered_courses_filters_kb(current_filters: GetManyCoursesFilters) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Искать по названию', callback_data='actor_registered_courses_filters-title')],
            [
                InlineKeyboardButton(text='Назад', callback_data='actor_registered_courses_filters-back'),
                InlineKeyboardButton(text='Применить', callback_data='actor_registered_courses_filters-apply'),
            ]
        ]
    )

    if current_filters.title:
        kb.inline_keyboard[0] = [
            InlineKeyboardButton(
                text=f'Искать по названию (Текущее: {current_filters.title})',
                callback_data='actor_registered_courses_filters-title',
            ),
        ]
        kb.inline_keyboard.insert(
            1, [InlineKeyboardButton(text='Сбросить', callback_data='actor_registered_courses_filters-reset')],
        )

    return kb
