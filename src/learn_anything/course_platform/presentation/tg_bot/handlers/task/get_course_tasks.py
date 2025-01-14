from contextlib import suppress
from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from learn_anything.course_platform.application.input_data import Pagination
from learn_anything.course_platform.application.interactors.task.get_course_tasks import GetCourseTasksInteractor, \
    GetCourseTasksInputData, AnyTaskData
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.presentors.tg_bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard
from learn_anything.course_platform.presentors.tg_bot.texts.get_task import get_task_text

router = Router()

DEFAULT_LIMIT = 10


@router.callback_query(
    F.data.startswith('get_course_tasks-'),
    F.message.as_('callback_query_message'),
    F.data.as_('callback_query_data'),
)
async def get_course_tasks(
        callback_query: CallbackQuery,
        state: FSMContext,
        callback_query_message: Message,
        callback_query_data: str,
        bot: Bot,
        interactor: FromDishka[GetCourseTasksInteractor],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()
    back_to, course_id = callback_query_data.split('-')[1:]

    await state.update_data(
        back_to=back_to,
        course_id=course_id,
    )

    pointer = data.get(f'course_{course_id}_tasks_pointer', 0)
    offset = data.get(f'course_{course_id}_tasks_offset', 0)

    output_data = await interactor.execute(
        GetCourseTasksInputData(
            course_id=CourseID(int(course_id)),
            pagination=Pagination(offset=offset, limit=DEFAULT_LIMIT),
        )
    )
    tasks = data.get(f'course_{course_id}_tasks', output_data.tasks)
    tasks[offset: offset + DEFAULT_LIMIT] = output_data.tasks

    total = output_data.total

    data = await state.update_data(
        {
            f'course_{course_id}_tasks': tasks,
            f'course_{course_id}_tasks_pointer': pointer,
            f'course_{course_id}_tasks_offset': offset,
            f'course_{course_id}_tasks_total': output_data.total,
        },
    )

    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    current_course = data['target_course']
    if total == 0:
        msg_text = 'Тут еще нет ни одного задания'
        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_course_tasks_keyboard(
                pointer=pointer,
                total=total,
                back_to=back_to,
                course_id=course_id,
                user_has_write_access=current_course.user_has_write_access
            )
        )
        return

    pointer = data[f'course_{course_id}_tasks_pointer']
    current_task = tasks[pointer]

    await bot.send_message(
        chat_id=user_id,
        text=get_task_text(current_task),
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_data=current_task,
            user_has_write_access=current_course.user_has_write_access,
            course_is_published=current_course.is_published,
            user_is_registered=current_course.user_is_registered,
        ),
        parse_mode='HTML'
    )


@router.callback_query(
    (F.data.startswith('course_tasks-next')) | (F.data.startswith('course_tasks-prev')),
    F.data.as_('callback_query_data'),
    F.message.as_('callback_query_message')
)
async def watch_course_tasks_prev_or_next(
        callback_query: CallbackQuery,
        callback_query_data: str,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetCourseTasksInteractor],
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()
    command, back_to, course_id = callback_query_data.split('-')[1:]

    pointer = data[f'course_{course_id}_tasks_pointer']
    tasks: list[AnyTaskData] = data[f'course_{course_id}_tasks']
    offset: int = data[f'course_{course_id}_tasks_offset']
    total = data[f'course_{course_id}_tasks_total']

    if command == 'next':
        if (pointer + 1) == offset + DEFAULT_LIMIT:
            output_data = await interactor.execute(
                GetCourseTasksInputData(
                    course_id=CourseID(int(course_id)),
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                )
            )

            tasks.extend(output_data.tasks)
            await state.update_data(
                {
                    f'course_{course_id}_tasks': tasks,
                    f'course_{course_id}_tasks_offset': offset + DEFAULT_LIMIT,
                    f'course_{course_id}_tasks_total': output_data.total,
                },
            )

        pointer += 1
    else:
        pointer -= 1

    current_task = tasks[pointer]
    current_course = data['target_course']

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query_message.message_id,
        text=get_task_text(current_task),
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_data=current_task,
            user_has_write_access=current_course.user_has_write_access,
            course_is_published=current_course.is_published,
            user_is_registered=current_course.user_is_registered,
        ),
        parse_mode='HTML'
    )

    await state.update_data(
        {
            f'course_{course_id}_tasks_pointer': pointer,
        }
    )
