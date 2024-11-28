from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka

from learn_anything.application.input_data import Pagination
from learn_anything.application.interactors.submission.get_many_submissions import GetActorSubmissionsInteractor, \
    GetManySubmissionsInputData, SubmissionData
from learn_anything.application.ports.data.submission_gateway import GetManySubmissionsFilters, SortBy
from learn_anything.entities.task.models import TaskID
from learn_anything.presentors.tg_bot.keyboards.submission.many_submissions import get_many_submissions_keyboard
from learn_anything.presentors.tg_bot.texts.get_many_submissions import get_actor_submissions_text

router = Router()

DEFAULT_FILTERS = GetManySubmissionsFilters(sort_by=SortBy.DATE)
DEFAULT_LIMIT = 10


@router.callback_query(F.data.startswith('get_my_submissions'))
async def get_my_submissions(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorSubmissionsInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    task_id, course_id, back_to = callback_query.data.split('-')[1], data['course_id'], data['back_to']
    filters = data.get(f'actor_submissions_{task_id}_filters', DEFAULT_FILTERS)
    pointer: int = data.get(f'actor_submissions_{task_id}_pointer', 0)
    offset: int = data.get(f'actor_submissions_{task_id}_offset', 0)

    output_data = await interactor.execute(
        data=GetManySubmissionsInputData(
            task_id=TaskID(int(task_id)),
            pagination=Pagination(offset=offset, limit=DEFAULT_LIMIT),
            filters=filters,
        )
    )

    submissions = data.get(f'actor_submissions_{task_id}', output_data.submissions)
    data = await state.update_data(
        **{
            f'actor_submissions_{task_id}': submissions,
            f'actor_submissions_{task_id}_pointer': pointer,
            f'actor_submissions_{task_id}_offset': offset,
            f'actor_submissions_{task_id}_total': output_data.total,
            f'actor_submissions_{task_id}_filters': filters,
            'task_id': task_id,
        }
    )

    total = output_data.total

    if total == 0:
        msg_text = 'Вы еще ни разу не решали эту задачу'

        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_many_submissions_keyboard(
                pointer=pointer,
                total=total,
                back_to=back_to,
                course_id=course_id
            )
        )

    pointer = data[f'actor_submissions_{task_id}_pointer']
    current_submission = submissions[pointer]
    text = get_actor_submissions_text(current_submission, pointer=pointer)

    await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=get_many_submissions_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id
        ),
        parse_mode='markdown'
    )


@router.callback_query(F.data.in_(['actor_submissions-next', 'actor_submissions-prev']))
async def watch_actor_submissions_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetActorSubmissionsInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to = data['back_to']
    course_id = data['course_id']
    task_id: str = data['task_id']

    command = callback_query.data.split('-')[1]

    pointer = data[f'actor_submissions_{task_id}_pointer']
    submissions: list[SubmissionData] = data[f'actor_submissions_{task_id}']
    offset: int = data[f'actor_submissions_{task_id}_offset']
    total = data[f'actor_submissions_{task_id}_total']
    filters = data.get(f'actor_submissions_{task_id}_filters', DEFAULT_FILTERS)

    if command == 'next':
        if (pointer + 1) == (offset + DEFAULT_LIMIT):
            output_data = await interactor.execute(
                data=GetManySubmissionsInputData(
                    task_id=TaskID(int(task_id)),
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                    filters=filters,
                )
            )

            submissions.extend(output_data.submissions)
            await state.update_data(
                **{
                    f'actor_submissions_{task_id}': submissions,
                    f'actor_submissions_{task_id}_pointer': 0,
                    f'actor_submissions_{task_id}_offset': offset + DEFAULT_LIMIT,
                    f'actor_submissions_{task_id}_total': output_data.total,
                    f'actor_submissions_{task_id}_filters': filters,
                }
            )

        pointer += 1
    else:
        pointer -= 1

    await state.update_data(
        **{f'actor_submissions_{task_id}_pointer': pointer}
    )

    current_submission = submissions[pointer]
    text = get_actor_submissions_text(current_submission, pointer=pointer)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=get_many_submissions_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id
        ),
        parse_mode='markdown'
    )
