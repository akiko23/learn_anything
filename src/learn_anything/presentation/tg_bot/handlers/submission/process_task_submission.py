from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka import FromDishka

from learn_anything.application.interactors.submission.create_submission import CreateCodeTaskSubmissionInteractor, \
    CreateCodeTaskSubmissionInputData
from learn_anything.application.interactors.task.get_course_tasks import TaskData
from learn_anything.entities.task.models import TaskType
from learn_anything.presentors.tg_bot.keyboards.task.do_course_task import get_do_task_kb
from learn_anything.presentors.tg_bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard
from learn_anything.presentation.tg_bot.states.submission import SubmissionForm
from learn_anything.presentors.tg_bot.texts.get_task import get_task_text
from learn_anything.presentors.tg_bot.texts.submission import get_on_failed_code_submission_text

router = Router()


@router.message(StateFilter(SubmissionForm.get_for_code), F.text)
async def process_code_task_submission(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateCodeTaskSubmissionInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    target_task: TaskData = data['target_task']
    submission = msg.text

    output_data = await interactor.execute(
        data=CreateCodeTaskSubmissionInputData(
            task_id=target_task.id,
            submission=submission
        )
    )

    if output_data.failed_output:
        text = get_on_failed_code_submission_text(output_data)
        return await msg.answer(
            text=text,
            reply_markup=get_do_task_kb(),
            parse_mode='markdown',
        )

    await state.set_state(state=None)

    course_id = data['course_id']
    back_to = data['back_to']

    tasks = data[f'course_{course_id}_tasks']
    pointer = data[f'course_{course_id}_tasks_pointer']
    total = data[f'course_{course_id}_tasks_total']
    current_course = data['target_course']

    tasks[pointer].solved_by_actor = True
    tasks[pointer].total_correct_submissions += 1
    tasks[pointer].total_submissions += 1

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await msg.answer(
        f'Поздравляем! Задача \'{target_task.title}\' решена'
    )

    await bot.send_message(
        chat_id=user_id,
        text=get_task_text(target_task),
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_id=target_task.id,
            user_has_write_access=current_course.user_has_write_access,
            user_is_registered=current_course.user_is_registered,
            course_is_published=current_course.is_published,
            task_is_practice=target_task.type != TaskType.THEORY
        ),
    )

