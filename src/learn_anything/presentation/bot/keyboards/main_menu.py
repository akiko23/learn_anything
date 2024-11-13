from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.entities.user.models import UserRole, UserID


def get_main_menu_keyboard(user_role: UserRole):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Все курсы', callback_data='main_menu-all_courses'),
            InlineKeyboardButton(text='Сейчас прохожу', callback_data='main_menu-get_registered_courses')],
        [
            InlineKeyboardButton(text='Создать курс', callback_data='main_menu-create_course'),
        ],
        [
            InlineKeyboardButton(text='Созданные курсы', callback_data='main_menu-get_created_courses'),
            InlineKeyboardButton(text='Совместные курсы', callback_data='main_menu-get_shared_courses'),
        ]
    ])

    if user_role in (UserRole.MODERATOR, UserRole.BOT_OWNER):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text='Создать ссылку для входа', callback_data='main_menu-create_auth_link'),
            InlineKeyboardButton(text='Инвалидировать ссылку', callback_data='main_menu-invalidate_auth_link')
        ])

    return kb
