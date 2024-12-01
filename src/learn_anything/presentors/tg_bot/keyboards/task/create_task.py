from collections.abc import Sequence

from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.enums import TaskType


def cancel_course_task_creation_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )


def get_course_task_topic_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Пропустить', callback_data=f'create_course_task_skip_topic')],
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )


def get_course_task_type_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Теория', callback_data=f'create_course_task_type-{TaskType.THEORY}')],
            [
                InlineKeyboardButton(text='Код', callback_data=f'create_course_task_type-{TaskType.CODE}'),
                InlineKeyboardButton(text='Текстовый ввод',
                                     callback_data=f'create_course_task_type-{TaskType.TEXT_INPUT}'),
                InlineKeyboardButton(text='Опрос', callback_data=f'create_course_task_type-{TaskType.POLL}'),
            ],
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )


def get_course_task_attempts_limit_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Пропустить', callback_data=f'create_course_task_skip_attempts_limit')],
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )


def get_code_task_prepared_code_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Пропустить', callback_data=f'create_course_task_skip_prepared_code')],
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )


def get_code_duration_timeout_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Пропустить', callback_data=f'create_course_task_skip_code_timeout')],
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )


def get_code_task_tests_kb(current_tests: Sequence[str]):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data=f'create_course_task_cancel')]
        ]
    )

    if len(current_tests) >= 1:
        kb.inline_keyboard.insert(
            0,
            [InlineKeyboardButton(text='Завершить', callback_data=f'create_course_task_finish')]
        )
    return kb


def after_course_task_creation_menu(
        course_id: CourseID,
        back_to: str
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Вернуться к курсу', callback_data=f'course-{back_to}-{course_id}')],
            [InlineKeyboardButton(text='К заданиям', callback_data=f'get_course_tasks-{back_to}-{course_id}')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )
