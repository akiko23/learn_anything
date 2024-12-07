from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka

from learn_anything.application.interactors.task.delete_task import DeleteTaskInteractor, DeleteTaskInputData
from learn_anything.domain.task.models import TaskID
from learn_anything.presentors.tg_bot.keyboards.task.delete_task import get_task_after_deletion_menu_kb

router = Router()


@router.callback_query(F.data.startswith('delete_task-'))
async def delete_task(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[DeleteTaskInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = data['back_to'], data['course_id']
    task_id = callback_query.data.split('-')[1]

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await interactor.execute(
        data=DeleteTaskInputData(task_id=TaskID(int(task_id)))
    )

    pointer = data[f'course_{course_id}_tasks_pointer']
    await state.update_data(
        **{f'course_{course_id}_tasks_pointer': max(0, pointer - 1)}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Задание успешно удалено',
        reply_markup=get_task_after_deletion_menu_kb(course_id=course_id, back_to=back_to),
    )
