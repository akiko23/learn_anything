from aiogram.types import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from learn_anything.course_platform.application.interactors.course.get_course import GetFullCourseOutputData


def get_course_kb(
        course_id: int,
        output_data: GetFullCourseOutputData,
        back_to: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if output_data.is_published:
        if output_data.user_is_registered:
            builder.row(
                InlineKeyboardButton(text='Проходить', callback_data=f'get_course_tasks-{back_to}-{course_id}'),
                InlineKeyboardButton(text='Покинуть', callback_data=f'leave_course-{back_to}-{course_id}'),
            )
        else:
            if (
                    (not output_data.registrations_limit)
                    or (output_data.total_registered + 1 <= output_data.registrations_limit)
            ):
                builder.row(InlineKeyboardButton(text='Записаться', callback_data=f'register_for_course-{back_to}-{course_id}'))

    if output_data.user_has_write_access:
        builder.row(
            InlineKeyboardButton(text='Панель управления', callback_data=f'edit_course-{back_to}-{course_id}'),
        )

    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'get_course-back_to_{back_to}'))

    return builder.as_markup()
