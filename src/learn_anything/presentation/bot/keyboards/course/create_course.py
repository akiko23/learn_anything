from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.entities.course.models import CourseID

CANCEL_COURSE_CREATION_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='create_course-cancel')]
    ]
)

GET_COURSE_PHOTO_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Пропустить', callback_data='create_course-skip_photo'),
            InlineKeyboardButton(text='Отмена', callback_data='create_course-cancel')
        ]
    ]
)

GET_COURSE_REGISTRATIONS_LIMIT_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Пропустить', callback_data='create_course-skip_registrations_limit'),
            InlineKeyboardButton(text='Отмена', callback_data='create_course-cancel')
        ]
    ]
)


def after_course_creation_menu(new_course_id: CourseID):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Перейти к курсу', callback_data=f'course-created_courses-{new_course_id}')],
            [InlineKeyboardButton(text='В главное меню', callback_data='all_courses-to_main_menu')],
        ]
    )
