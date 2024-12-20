from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_many_submissions_keyboard(
        pointer: int,
        total: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='actor_submissions_back_to_task')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='actor_submissions-prev'),
            InlineKeyboardButton(text='➡️', callback_data='actor_submissions-next'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data='actor_submissions-next'),
        ])

    if (pointer + 1 == total) and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data='actor_submissions-prev'),
        ])

    return kb
