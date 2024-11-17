from typing import Any

from aiogram.fsm.context import FSMContext

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from dishka import FromDishka

from learn_anything.application.input_data import Pagination

from learn_anything.application.interactors.task.get_course_tasks import GetCourseTasksInteractor, \
    GetCourseTasksInputData, TaskData
from learn_anything.entities.course.models import CourseID

from learn_anything.presentation.bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard

router = Router()

DEFAULT_LIMIT = 10
DEFAULT_FILTERS = lambda: None


@router.callback_query(F.data.startswith('get_course_tasks-'))
async def get_course_tasks(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetCourseTasksInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    output_data = await interactor.execute(
        GetCourseTasksInputData(
            course_id=CourseID(int(course_id)),
            pagination=Pagination(offset=0, limit=DEFAULT_LIMIT),
        )
    )

    pointer = data.get(f'course_{course_id}_tasks_pointer', 0)
    offset = data.get(f'course_{course_id}_tasks_offset', 0)

    data = await state.update_data(
        **{
            f'course_{course_id}_tasks': output_data.tasks,
            f'course_{course_id}_tasks_pointer': pointer,
            f'course_{course_id}_tasks_offset': offset,
            f'course_{course_id}_tasks_total': output_data.total,
        },
    )

    tasks = output_data.tasks
    total = output_data.total

    if total == 0:
        msg_text = 'Вы еще не создали ни одного задания'
        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_course_tasks_keyboard(
                pointer=pointer,
                total=total,
                back_to=back_to,
                course_id=course_id,
            )
        )
        return

    pointer = data['created_courses_pointer']
    current_task = tasks[pointer]
    await bot.send_message(
        chat_id=user_id,
        text=f"""Заголовок: {current_task.title}

Тело: {current_task.body}

Создано: {current_task.created_at}
""",
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_id=current_task.id
        ),
    )


@router.callback_query((F.data.startswith('course_tasks-next')) | (F.data.startswith('course_tasks-prev')))
async def watch_course_tasks_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetCourseTasksInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    command, back_to, course_id = callback_query.data.split('-')[1:]

    pointer = data[f'course_{course_id}_tasks_pointer']
    tasks: list[TaskData] = data[f'course_{course_id}_tasks']
    offset: int = data[f'course_{course_id}_tasks_offset']
    total = data[f'course_{course_id}_tasks_total']

    if command == 'next':
        if (pointer + 1) % DEFAULT_LIMIT == 0:
            output_data = await interactor.execute(
                GetCourseTasksInputData(
                    course_id=CourseID(int(course_id)),
                    pagination=Pagination(offset=offset + DEFAULT_LIMIT, limit=DEFAULT_LIMIT),
                )
            )

            tasks.extend(output_data.tasks)
            await state.update_data(
                **{
                    f'course_{course_id}_tasks': tasks,
                    f'course_{course_id}_tasks_offset': offset + DEFAULT_LIMIT,
                    f'course_{course_id}_tasks_total': output_data.total,
                },
            )

        pointer += 1

    else:
        pointer -= 1

    await state.update_data(
        **{
            f'course_{course_id}_tasks_pointer': pointer,
        }
    )

    current_task = tasks[pointer]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=f"""Заголовок: {current_task.title}

Тело: {current_task.body}

Создано: {current_task.created_at}
""",
        reply_markup=get_course_tasks_keyboard(
            pointer=pointer,
            total=total,
            back_to=back_to,
            course_id=course_id,
            task_id=current_task.id,
        ),
    )

