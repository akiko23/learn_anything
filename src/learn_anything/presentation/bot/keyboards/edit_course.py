from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_course_edit_menu_kb(course_id: int, back_to: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Задания", callback_data=f'get_course_tasks-{course_id}')],
            [InlineKeyboardButton(text="Назад", callback_data=f'edit_course_back_to-{back_to}-{course_id}')],
        ]
    )
