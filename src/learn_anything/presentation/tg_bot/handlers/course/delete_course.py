from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.presentation.tg_bot.keyboards.course.delete_course import get_course_pre_delete_menu_kb, \
    get_course_after_deletion_menu_kb
from learn_anything.presentation.tg_bot.keyboards.course.edit_course import get_course_edit_menu_kb

router = Router()


@router.callback_query(F.data.startswith('delete_course-'))
async def pre_deletion_menu(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await bot.send_message(
        chat_id=user_id,
        text='Вы уверены, что хотите удалить курс? Все данные будут потеряны',
        reply_markup=get_course_pre_delete_menu_kb(
            course_id=course_id,
            back_to=back_to
        ),
    )



@router.callback_query(F.data.startswith('absolutely_delete_course-'))
async def delete_course(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[DeleteCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await interactor.execute(
        data=DeleteCourseInputData(course_id=course_id)
    )

    await bot.send_message(
        chat_id=user_id,
        text='Курс успешно удален',
        reply_markup=get_course_after_deletion_menu_kb(
            course_id=course_id,
            back_to=back_to
        ),
    )


