from random import sample
from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from dishka import FromDishka

from learn_anything.application.interactors.task.get_task import GetTaskInteractor, GetTaskInputData
from learn_anything.entities.task.models import TaskID, TaskType
from learn_anything.presentation.tg_bot.keyboards.task.do_course_task import get_do_task_kb
from learn_anything.presentation.tg_bot.states.submission import SubmissionForm

router = Router()


@router.callback_query(F.data.startswith('do_course_task-'))
async def do_course_task(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        # interactor: FromDishka[GetTaskInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    # task_id = callback_query.data.split('-')[1]
    course_id = data['course_id']

    tasks = data[f'course_{course_id}_tasks']
    target_task = tasks[data[f'course_{course_id}_tasks_pointer']]

    if target_task.type == TaskType.CODE:
        await state.set_state(state=SubmissionForm.get_for_code)
        await bot.send_message(chat_id=user_id, text='Отправьте решение', reply_markup=get_do_task_kb())



@router.callback_query(StateFilter(SubmissionForm), F.data == 'stop_doing_task')
async def cancel_doing_task(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.set_state(state=None)

    await callback_query.answer('Вы отменили выполнение задания')
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)



