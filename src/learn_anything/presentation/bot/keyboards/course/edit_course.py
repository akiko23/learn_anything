from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData


def get_course_edit_menu_kb(course: GetFullCourseOutputData, back_to: str):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Задания", callback_data=f'get_course_tasks-{back_to}-{course.id}')],
            [
                InlineKeyboardButton(text="Удалить", callback_data=f'delete_course-{back_to}-{course.id}'),
            ],
            [InlineKeyboardButton(text="Назад", callback_data=f'course-{back_to}-{course.id}')],
        ]
    )

    if not course.is_published:
        kb.inline_keyboard[1].insert(
            0,
            InlineKeyboardButton(text='Опубликовать', callback_data=f'publish_course-{back_to}-{course.id}')
        )
    return kb


