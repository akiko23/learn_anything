from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.application.interactors.task.get_task import GetTaskInputData, GetTaskInteractor
from learn_anything.entities.task.models import TaskID
from learn_anything.presentation.bot.keyboards.task.get_course_tasks import get_course_tasks_keyboard
from learn_anything.presentation.bot.keyboards.task.get_task import get_course_task_kb

router = Router()



# @router.callback_query(F.data == 'get_course_task-back_to_course_tasks')
# async def back_to_course_tasks(
#         callback_query: CallbackQuery,
#         state: FSMContext,
#         bot: Bot,
# ):
#     user_id: int = callback_query.from_user.id
#     data: dict[str, Any] = await state.get_data()
#
#     back_to, course_id = data['back_to'], data['course_id']
#
#     await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
#
#     tasks = data[f'course_{course_id}_tasks']
#     pointer = data[f'course_{course_id}_tasks_pointer']
#     total = data[f'course_{course_id}_tasks_total']
#
#     current_task = tasks[pointer]
#     await bot.send_message(
#         chat_id=user_id,
#         text=f"""Заголовок: {current_task.title}
#
# Тип: {current_task.type}
#
# Тело: {current_task.body}
#
# Порядковый номер в курсе: {current_task.index_in_course}
#
# Создано: {current_task.created_at}
# """,
#         reply_markup=get_course_tasks_keyboard(
#             pointer=pointer,
#             total=total,
#             back_to=back_to,
#             course_id=course_id,
#             task_id=current_task.id,
#             actor_is_registered=data[f'course_{course_id}_registered'],
#         ),
#     )
#
#     del (
#         data['back_to'],
#         data['course_id']
#     )
#     await state.set_data(data)
#
