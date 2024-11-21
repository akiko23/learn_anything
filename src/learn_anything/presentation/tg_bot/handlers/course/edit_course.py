from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.presentation.tg_bot.keyboards.course.edit_course import get_course_edit_menu_kb

router = Router()


@router.callback_query(F.data.startswith('edit_course-'))
async def get_course_edit_menu(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    course = await interactor.execute(
        data=GetCourseInputData(
            course_id=CourseID(int(course_id))
        )
    )

    if callback_query.message.text:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=callback_query.message.text + '\nВыберите, что хотите изменить',
            reply_markup=get_course_edit_menu_kb(
                course=course,
                back_to=back_to
            ),
        )
    else:
        await bot.edit_message_caption(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            caption=callback_query.message.caption + '\nВыберите, что хотите изменить',
            reply_markup=get_course_edit_menu_kb(
                course=course,
                back_to=back_to,
            ),
        )

