from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.course.delete_course import DeleteCourseInteractor, DeleteCourseInputData
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.delete_course import get_course_pre_delete_menu_kb, \
    get_course_after_deletion_menu_kb

router = Router()


@router.callback_query(
    F.data.startswith('delete_course-'),
    F.data.as_('callback_query_data'),
    F.message.as_('callback_query_message')
)
async def pre_deletion_menu(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        callback_query_data: str,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id
    back_to, course_id = callback_query_data.split('-')[1:]

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    await bot.send_message(
        chat_id=user_id,
        text='Вы уверены, что хотите удалить курс? Все данные будут потеряны',
        reply_markup=get_course_pre_delete_menu_kb(
            course_id=course_id,
            back_to=back_to
        ),
    )


@router.callback_query(
    F.data.startswith('absolutely_delete_course-'),
    F.data.as_('callback_query_data'),
    F.message.as_('callback_query_message')
)
async def delete_course(
        callback_query: CallbackQuery,
        callback_query_data: str,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[DeleteCourseInteractor],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()
    back_to, course_id = callback_query_data.split('-')[1:]  # noqa

    await interactor.execute(
        data=DeleteCourseInputData(course_id=CourseID(int(course_id)))
    )

    pointer = data[f'{back_to}_pointer']
    await state.update_data(
        {
            'registered_courses_pointer': max(0, pointer - 1),
            'created_courses_pointer': max(0, pointer - 1),
            'all_courses_pointer': max(0, pointer - 1)
        }
    )

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text='Курс успешно удален',
        reply_markup=get_course_after_deletion_menu_kb(),
    )
