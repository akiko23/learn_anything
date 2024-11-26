from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka import FromDishka

from learn_anything.application.interactors.submission.create_submission import CreateCodeTaskSubmissionInteractor, \
    CreateCodeTaskSubmissionInputData
from learn_anything.entities.task.models import TaskType
from learn_anything.presentors.tg_bot.keyboards.task.do_course_task import get_do_task_kb
from learn_anything.presentors.tg_bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard
from learn_anything.presentation.tg_bot.states.submission import SubmissionForm

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

    target_task = data['target_task']
    submission = msg.text

    output_data = await interactor.execute(
        data=CreateCodeTaskSubmissionInputData(
            task_id=target_task.id,
            submission=submission
        )
    )

    if output_data.failed_output:
        if output_data.failed_test_idx == -1:
            print(output_data.failed_output)
            return await msg.answer(
                text='Решение не прошло проверку, попробуйте еще раз\n\n'
                     f'```\n{output_data.failed_output[:500] + '...'}```',
                reply_markup=get_do_task_kb(),
                parse_mode='markdown',
            )
        return await msg.answer(
            text='Решение не прошло проверку, попробуйте еще раз\n\n'
                 f'Тест #{output_data.failed_test_idx + 1} провалился:\n'
                 f'```\n{output_data.failed_output}```',
            reply_markup=get_do_task_kb(),
            parse_mode='markdown',
        )

    await state.set_state(state=None)

    course_id = data['course_id']
    back_to = data['back_to']

    tasks = data[f'course_{course_id}_tasks']
    task_data = tasks[data[f'course_{course_id}_tasks_pointer']]
    pointer = data[f'course_{course_id}_tasks_pointer']
    total = data[f'course_{course_id}_tasks_total']
    current_course = data['target_course']

    await msg.answer(f'Поздравляем! Задача \'{task_data.title}\' решена')

    task_topic = 'Без темы'
    if task_data.topic:
        task_topic = f'Тема: {task_data.topic}'

    await bot.send_message(
        chat_id=user_id,
        text=(
            f'{task_data.title}\n'
            f'\n'
            f'Тип: Задание на код\n'
            f'\n'
            f'{task_topic}\n'
            f'\n'
            f'Тело: {task_data.body}\n'
            f'\n'
            f'Макс. время выполнения: {task_data.code_duration_timeout} с.\n'
            f'\n'
            f'Решений отправлено: {task_data.total_submissions}\n'
            f'\n'
            f'Создано: {task_data.created_at}\n'
        ),
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_id=task_data.id,
            user_has_write_access=current_course.user_has_write_access,
            user_is_registered=current_course.user_is_registered,
            course_is_published=current_course.is_published,
            task_is_practice=task_data.type != TaskType.THEORY
        ),
    )

