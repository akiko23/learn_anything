from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.entities.task.models import TaskID


def get_course_tasks_keyboard(
        pointer: int,
        total: int,
        back_to: str,
        course_id: str,
        task_id: TaskID | None = None
):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить задание', callback_data=f'create_course_task-{back_to}-{course_id}')
            ],
            [InlineKeyboardButton(text='Назад', callback_data=f'course-{back_to}-{course_id}')],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='Назад', callback_data=f'course_tasks-prev-{back_to}-{course_id}'),
            InlineKeyboardButton(text='Далее', callback_data=f'course_tasks-next-{back_to}-{course_id}'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='Далее', callback_data=f'course_tasks-next-{back_to}-{course_id}'),
        ])

    if (pointer + 1) == total and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='Назад', callback_data=f'course_tasks-prev-{back_to}-{course_id}'),
        ])

    if task_id:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(
                text='Перейти к заданию',
                callback_data=f'get_course_task-{back_to}-{course_id}-{task_id}'),
        ])

    return kb
