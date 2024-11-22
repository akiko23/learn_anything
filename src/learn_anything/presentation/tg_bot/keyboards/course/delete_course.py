from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_course_pre_delete_menu_kb(course_id: str, back_to: str):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Все равно удалить", callback_data=f'absolutely_delete_course-{back_to}-{course_id}')],
            [InlineKeyboardButton(text="Назад", callback_data=f'course-{back_to}-{course_id}')],
        ]
    )

    return kb


def get_course_after_deletion_menu_kb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="В главное меню", callback_data='all_courses-to_main_menu')],
        ]
    )

    return kb

