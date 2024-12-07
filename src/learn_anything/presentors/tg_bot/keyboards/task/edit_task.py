from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from learn_anything.application.interactors.task.get_course_tasks import TaskData
from learn_anything.domain.task.enums import TaskType
from learn_anything.domain.task.models import TaskID


def get_task_edit_menu_kb(
        task: TaskData,
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

    if task.type != TaskType.THEORY:
        if task.type == TaskType.CODE:
            builder.row(
                InlineKeyboardButton(text="Тесты", callback_data=f'get_code_task_tests-{task.id}'),
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
            InlineKeyboardButton(text="Изменить количество попыток", callback_data=f'edit_task_attempts_limit-{task.id}'),
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


def get_attempts_limit_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Убрать", callback_data='task_attempts_limit_set_null')],
            [InlineKeyboardButton(text="Отмена", callback_data='cancel_task_editing')],
        ]
    )


def watch_code_task_tests_kb(pointer: int, total: int, task_id: TaskID):
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    if 0 < pointer < (total - 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data=f'code_task_tests-prev-{task_id}'),
            InlineKeyboardButton(text='➡️', callback_data=f'code_task_tests-next-{task_id}'),
        ])

    if pointer == 0 and total > 1:
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='➡️', callback_data=f'code_task_tests-next-{task_id}'),
        ])

    if (pointer + 1) == total and (total > 1):
        kb.inline_keyboard.insert(0, [
            InlineKeyboardButton(text='⬅️', callback_data=f'code_task_tests-prev-{task_id}'),
        ])


    kb.inline_keyboard.insert(0, [
        InlineKeyboardButton(text='Добавить тест', callback_data=f'add_code_task_test-{task_id}'),
        InlineKeyboardButton(text='Изменить код', callback_data=f'edit_code_task_test-{task_id}'),
    ])

    if total > 1:
        kb.inline_keyboard[0].insert(
            0,
            InlineKeyboardButton(text='Удалить', callback_data=f'delete_code_task_test-{task_id}'),
        )
    kb.inline_keyboard.append([
        InlineKeyboardButton(text='Назад', callback_data=f'edit_task-{task_id}'),
    ])

    return kb

