from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from learn_anything.application.interactors.task.get_task import GetTaskOutputData


def get_course_task_kb(
        course_id: int,
        task_id: int,
        output_data: GetTaskOutputData,
        back_to: str,
        user_is_registered: bool,
        pointer: int,
        total: int,
):
    builder = InlineKeyboardBuilder()

    if user_is_registered:
        builder.row(
            InlineKeyboardButton(text='Пройти задание', callback_data=f'start_doing_task-{task_id}'),
        )
        builder.row(
            InlineKeyboardButton(text='Мои решения', callback_data=f'submissions-{task_id}'),
        )

    if output_data.user_has_write_access:
        builder.row(
            InlineKeyboardButton(text='Изменить задание', callback_data=f'edit_task-{task_id}'),
        )

    kb = builder.as_markup()
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

    builder.row(InlineKeyboardButton(text='Назад', callback_data='get_course_task-back_to_course_tasks'))

    return builder.as_markup()
