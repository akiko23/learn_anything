import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


IDE_BASE_URL = os.environ.get("IDE_URL", "https://learn-anything.ru/ide")


def get_do_task_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='stop_doing_task')]
        ]
    )
    return kb


def get_do_code_task_kb(task_id: int) -> InlineKeyboardMarkup:
    """Keyboard for code tasks — includes WebApp IDE button."""
    ide_url = f"{IDE_BASE_URL}?task_id={task_id}"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🐍 Открыть IDE',
                    web_app=WebAppInfo(url=ide_url),
                )
            ],
            [InlineKeyboardButton(text='✏️ Отправить текстом', callback_data='solve_code_via_text')],
            [InlineKeyboardButton(text='✕ Отмена', callback_data='stop_doing_task')],
        ]
    )
    return kb


def no_attempts_left_kb(back_to: str, course_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='К заданию', callback_data=f'get_course_tasks-{back_to}-{course_id}')]
        ]
    )
    return kb
