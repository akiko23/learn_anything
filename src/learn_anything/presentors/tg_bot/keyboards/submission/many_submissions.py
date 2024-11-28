from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_many_submissions_keyboard(
        pointer: int,
        total: int,
        back_to: str,
        course_id: str
):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=f'get_course_tasks-{back_to}-{course_id}')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data=f'actor_submissions-prev'),
            InlineKeyboardButton(text='➡️', callback_data=f'actor_submissions-next'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data=f'actor_submissions-next'),
        ])

    if (pointer + 1 == total) and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data=f'actor_submissions-prev'),
        ])

    return kb
