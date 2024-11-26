from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from learn_anything.application.interactors.task.get_course_tasks import AnyTaskData, PracticeTaskData, CodeTaskData


def get_task_edit_menu_kb(
        task: AnyTaskData,
        course_id: str,
        back_to: str
):
    base_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить название", callback_data=f'edit_task_title-{task.id}'),
                InlineKeyboardButton(text="Изменить тему", callback_data=f'edit_task_topic-{task.id}'),
            ],
            [
                InlineKeyboardButton(text="Изменить описание", callback_data=f'edit_task_body-{task.id}'),
            ],
        ]
    )
    builder = InlineKeyboardBuilder(base_kb.inline_keyboard)

    if isinstance(task, PracticeTaskData):
        if isinstance(task, CodeTaskData):
            builder.row(
                InlineKeyboardButton(text="Тесты", callback_data=f'get_task_tests-{task.id}'),
            )
            builder.row(
                InlineKeyboardButton(text="Решения пользователей", callback_data=f'get_all_task_submissions-{task.id}'),
            )
            builder.row(
                InlineKeyboardButton(text="Изменить таймаут", callback_data=f'edit_task_timeout-{task.id}'),
                InlineKeyboardButton(text="Изменить код инициализации",
                                     callback_data=f'edit_task_prepared_code-{task.id}'),
            )

        builder.row(
            InlineKeyboardButton(text="Изменить количество попыток", callback_data=f'edit_task_body-{task.id}'),
        )

    builder.row(InlineKeyboardButton(text="Удалить", callback_data=f'delete_task-{task.id}'))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=f'get_course_tasks-{back_to}-{course_id}'))

    return builder.as_markup()


CANCEL_EDITING_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data='cancel_task_editing')]
    ]
)


def get_task_after_edit_menu_kb(
        back_to: str,
        course_id: str,
):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=f'edit_task-{back_to}-{course_id}')],
            [
                InlineKeyboardButton(text="К курсу", callback_data=f'course-{back_to}-{course_id}'),
                InlineKeyboardButton(text="В главное меню", callback_data='all_courses-to_main_menu')
            ],
        ]
    )

    return kb
