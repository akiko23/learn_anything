from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from learn_anything.application.interactors.task.get_task import GetTaskOutputData


def get_do_task_kb():
    builder = InlineKeyboardBuilder()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='stop_doing_task')]
        ]
    )
    return kb
