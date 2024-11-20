from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from aiogram.types import BufferedInputFile

from learn_anything.application.interactors.course.create_course import CreateCourseInteractor, CreateCourseInputData
from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.application.interactors.course.register_for_course import RegisterForCourseInteractor, \
    RegisterForCourseInputData
from learn_anything.application.interactors.course.update_course import UpdateCourseInteractor, UpdateCourseInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.presentation.bot.keyboards.course.many_courses import get_all_courses_keyboard, \
    get_actor_registered_courses_keyboard, get_actor_created_courses_keyboard
from learn_anything.presentation.bot.keyboards.course.get_course import get_course_kb
from learn_anything.presentation.bot.keyboards.course.register_for_course import get_course_after_registration_menu

router = Router()


@router.callback_query(F.data.startswith('register_for_course-'))
async def register_for_course(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[RegisterForCourseInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    await interactor.execute(data=RegisterForCourseInputData(course_id=CourseID(int(course_id))))

    await callback_query.answer(text='Вы успешно зарегестрировались на курс')

    target_course = data['target_course']
    target_course.user_is_registered = True

    data = await state.update_data(
        **{
            f'course_{course_id}_registered': target_course.user_is_registered,
            'target_course': target_course,
        },
    )

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=get_course_kb(
            back_to=back_to,
            course_id=int(course_id),
            output_data=target_course
        )
    )
