from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData


def get_course_after_registration_menu(back_to: str, course_id: str):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="К курсу", callback_data=f'course-{back_to}-{course_id}')],
            [InlineKeyboardButton(text="В главное меню", callback_data=f'all_courses-to_main_menu')],
        ]
    )

    return kb


