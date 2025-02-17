from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.course.publish_course import PublishCourseInteractor, \
    PublishCourseInputData
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.get_course import get_course_kb

router = Router()


@router.callback_query(
    F.data.startswith('publish_course-'),
    F.data.as_('callback_query_data'),
    F.message.as_('callback_query_message')
)
async def publish_course(
        callback_query: CallbackQuery,
        callback_query_data: str,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[PublishCourseInteractor],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()
    back_to, course_id = callback_query_data.split('-')[1:]

    published_course = await interactor.execute(data=PublishCourseInputData(course_id=CourseID(int(course_id))))

    await callback_query.answer(text=f'Вы успешно опубликовали курс {published_course}')

    target_course = data['target_course']
    target_course.is_published = True

    data = await state.update_data(
        {
            'target_course': target_course,
        },
    )

    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query_message.message_id,
        reply_markup=get_course_kb(
            back_to=back_to,
            course_id=int(course_id),
            output_data=data['target_course']
        )
    )
