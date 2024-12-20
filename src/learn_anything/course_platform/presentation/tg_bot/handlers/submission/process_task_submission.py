from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.submission.create_submission import \
    CreateCodeTaskSubmissionInteractor, \
    CreateCodeTaskSubmissionInputData
from learn_anything.course_platform.application.interactors.task.get_course_tasks import CodeTaskData
from learn_anything.course_platform.presentation.tg_bot.states.submission import SubmissionForm
from learn_anything.course_platform.presentors.tg_bot.keyboards.task.do_course_task import get_do_task_kb, \
    no_attempts_left_kb
from learn_anything.course_platform.presentors.tg_bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard
from learn_anything.course_platform.presentors.tg_bot.texts.get_task import get_task_text
from learn_anything.course_platform.presentors.tg_bot.texts.submission import get_on_failed_code_submission_text

router = Router()


@router.message(
    StateFilter(SubmissionForm.get_for_code),
    F.text.as_('submission')
)
async def process_code_task_submission(
        msg: Message,
        submission: str,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateCodeTaskSubmissionInteractor],
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = data['back_to'], data['course_id']

    tasks = data[f'course_{course_id}_tasks']
    pointer = data[f'course_{course_id}_tasks_pointer']
    total = data[f'course_{course_id}_tasks_total']
    current_course = data['target_course']

    target_task: CodeTaskData = tasks[pointer]
    output_data = await interactor.execute(
        data=CreateCodeTaskSubmissionInputData(
            task_id=target_task.id,
            submission=submission
        )
    )

    try:
        target_task.total_submissions += 1
        target_task.total_actor_submissions += 1

        attempts_left = None
        if target_task.attempts_limit:
            attempts_left = max(target_task.attempts_limit - target_task.total_actor_submissions, 0)

        if output_data.failed_output and output_data.failed_test_idx:
            text = get_on_failed_code_submission_text(
                failed_test_output=output_data.failed_output,
                failed_test_idx=output_data.failed_test_idx,
                attempts_left=attempts_left
            )
            if attempts_left == 0:
                await state.set_state(state=None)
                await msg.answer(
                    text=text,
                    reply_markup=no_attempts_left_kb(
                        back_to=back_to,
                        course_id=course_id,
                    ),
                    parse_mode='HTML'
                )
                return

            await msg.answer(
                text=text,
                reply_markup=get_do_task_kb(),
                parse_mode='HTML'
            )
            return

        await state.set_state(state=None)

        target_task.solved_by_actor = True
        target_task.total_correct_submissions += 1

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
                task_data=target_task,
                user_has_write_access=current_course.user_has_write_access,
                user_is_registered=current_course.user_is_registered,
                course_is_published=current_course.is_published,
            ),
            parse_mode='HTML'
        )
    finally:
        tasks[pointer] = target_task
        await state.update_data(
            {f'course_{course_id}_tasks': tasks}
        )
