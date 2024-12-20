from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.task.delete_task import DeleteTaskInteractor, DeleteTaskInputData
from learn_anything.course_platform.domain.entities.task.models import TaskID
from learn_anything.course_platform.presentors.tg_bot.keyboards.task.delete_task import get_task_after_deletion_menu_kb

router = Router()


@router.callback_query(
    F.data.startswith('delete_task-'),
    F.data.as_('callback_query_data'),
    F.message.as_('callback_query_message'),
)
async def delete_task(
        callback_query: CallbackQuery,
        callback_query_data: str,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[DeleteTaskInteractor],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = data['back_to'], data['course_id']
    task_id = callback_query_data.split('-')[1]

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    await interactor.execute(
        data=DeleteTaskInputData(task_id=TaskID(int(task_id)))
    )

    pointer = data[f'course_{course_id}_tasks_pointer']
    await state.update_data(
        {f'course_{course_id}_tasks_pointer': max(0, pointer - 1)}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Задание успешно удалено',
        reply_markup=get_task_after_deletion_menu_kb(course_id=course_id, back_to=back_to),
    )
