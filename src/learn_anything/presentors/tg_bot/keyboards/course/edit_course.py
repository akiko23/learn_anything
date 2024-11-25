from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData


def get_course_edit_menu_kb(course: GetFullCourseOutputData, back_to: str):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Задания", callback_data=f'get_course_tasks-{back_to}-{course.id}')],
            [InlineKeyboardButton(text='Добавить задание', callback_data=f'create_course_task-{back_to}-{course.id}')],
            [
                InlineKeyboardButton(text="Изменить название",
                                     callback_data=f'edit_course_title-{back_to}-{course.id}'),
                InlineKeyboardButton(text="Изменить описание",
                                     callback_data=f'edit_course_description-{back_to}-{course.id}')
            ],
            [InlineKeyboardButton(text='Изменить фото', callback_data=f'edit_course_photo-{back_to}-{course.id}')],
            [
                InlineKeyboardButton(text="Удалить", callback_data=f'delete_course-{back_to}-{course.id}'),
            ],
            [InlineKeyboardButton(text="Назад", callback_data=f'course-{back_to}-{course.id}')],
        ]
    )

    if not course.is_published and course.total_tasks > 0:
        kb.inline_keyboard.insert(
            1,
            [InlineKeyboardButton(text='Опубликовать', callback_data=f'publish_course-{back_to}-{course.id}')]
        )
    return kb


CANCEL_EDITING_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data='cancel_course_editing')]
    ]
)


def get_course_after_edit_menu_kb(
        back_to: str,
        course_id: str,
):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=f'edit_course-{back_to}-{course_id}')],
            [
                InlineKeyboardButton(text="К курсу", callback_data=f'course-{back_to}-{course_id}'),
                InlineKeyboardButton(text="В главное меню", callback_data='all_courses-to_main_menu')
            ],
        ]
    )

    return kb
