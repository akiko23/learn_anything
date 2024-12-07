from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.application.interactors.task.get_course_tasks import TaskData
from learn_anything.domain.entities.task.enums import TaskType


def get_course_tasks_keyboard(
        pointer: int,
        total: int,
        back_to: str,
        course_id: str,
        user_has_write_access: bool | None = None,
        task_data: TaskData | None = None,
        course_is_published: bool | None = None,
        user_is_registered: bool | None = None,
):
    back_btn_callback_data = f'course-{back_to}-{course_id}'
    if user_has_write_access:
        back_btn_callback_data = f'edit_course-{back_to}-{course_id}'

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=back_btn_callback_data)],
        ]
    )

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data=f'course_tasks-prev-{back_to}-{course_id}'),
            InlineKeyboardButton(text='➡️', callback_data=f'course_tasks-next-{back_to}-{course_id}'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data=f'course_tasks-next-{back_to}-{course_id}'),
        ])

    if (pointer + 1) == total and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data=f'course_tasks-prev-{back_to}-{course_id}'),
        ])

    if not task_data:
        return kb

    # here we have a task
    if user_has_write_access:
        kb.inline_keyboard.insert(
            0,
            [InlineKeyboardButton(text='Панель управления', callback_data=f'edit_task-{task_data.id}')]
        )

    if task_data.type != TaskType.THEORY and course_is_published and user_is_registered:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(
                text='Пройти задание',
                callback_data=f'do_course_task-{task_data.id}'
            ),
            InlineKeyboardButton(
                text='Мои решения',
                callback_data=f'get_my_submissions-{task_data.id}'),
        ])
        if task_data.attempts_limit is not None and (task_data.attempts_limit - task_data.total_actor_submissions) == 0:
            kb.inline_keyboard[0].pop(0)

    return kb
