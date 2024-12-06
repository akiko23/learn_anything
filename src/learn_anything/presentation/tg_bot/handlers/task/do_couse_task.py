from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData
from learn_anything.entities.task.enums import TaskType
from learn_anything.presentors.tg_bot.texts.get_task import get_task_text
from learn_anything.presentors.tg_bot.keyboards.task.do_course_task import get_do_task_kb
from learn_anything.presentors.tg_bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard
from learn_anything.presentation.tg_bot.states.submission import SubmissionForm

router = Router()


@router.callback_query(F.data.startswith('do_course_task-'))
async def do_course_task(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    # task_id = callback_query.data.split('-')[1]
    course_id = data['course_id']

    tasks = data[f'course_{course_id}_tasks']
    target_task = tasks[data[f'course_{course_id}_tasks_pointer']]

    await state.update_data(
        target_task=target_task,
        msg_on_delete=callback_query.message.message_id,
    )

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

    course_id = data['course_id']
    back_to = data['back_to']

    tasks = data[f'course_{course_id}_tasks']
    task_data = tasks[data[f'course_{course_id}_tasks_pointer']]
    pointer = data[f'course_{course_id}_tasks_pointer']
    total = data[f'course_{course_id}_tasks_total']
    current_course: GetFullCourseOutputData = data['target_course']

    await bot.send_message(
        chat_id=user_id,
        text=get_task_text(task_data),
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_data=task_data,
            user_has_write_access=current_course.user_has_write_access,
            user_is_registered=current_course.user_is_registered,
            course_is_published=current_course.is_published,
        ),
    )
