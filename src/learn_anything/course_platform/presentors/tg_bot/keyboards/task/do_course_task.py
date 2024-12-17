from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_do_task_kb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='stop_doing_task')]
        ]
    )
    return kb


def no_attempts_left_kb(back_to, course_id):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='К заданию', callback_data=f'get_course_tasks-{back_to}-{course_id}')]
        ]
    )
    return kb
