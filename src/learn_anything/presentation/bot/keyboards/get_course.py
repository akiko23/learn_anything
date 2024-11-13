from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData
from learn_anything.entities.user.models import User, UserRole


def get_course_kb(
        course_id: int,
        output_data: GetFullCourseOutputData,
        back_to: str,
):
    builder = InlineKeyboardBuilder()

    if output_data.user_is_registered:
        builder.row(InlineKeyboardButton(text='Покинуть', callback_data=f'leave_course-{course_id}'))
    else:
        if (
                (not output_data.registrations_limit)
                or (output_data.total_registered + 1 <= output_data.registrations_limit)
        ):
            builder.row(InlineKeyboardButton(text='Записаться', callback_data=f'register_for_course-{course_id}'))

    if output_data.user_has_write_access:
        builder.row(
            InlineKeyboardButton(text='Редактировать', callback_data=f'edit_course-{back_to}-{course_id}'),
            InlineKeyboardButton(text='Удалить (Not Implemented)', callback_data=f'delete_course-{back_to}-{course_id}'),
        )

        builder.button(text='Опубликовать', callback_data=f'publish_course-{back_to}-{course_id}') if output_data.is_published else None

    builder.button(text='Назад', callback_data=f'get_course-back_to_{back_to}')

    return builder.as_markup()
