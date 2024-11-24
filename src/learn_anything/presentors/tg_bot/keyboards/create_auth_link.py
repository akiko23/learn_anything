from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


CANCEL_AUTH_LINK_CREATION_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='create_auth_link-cancel')]
    ]
)
