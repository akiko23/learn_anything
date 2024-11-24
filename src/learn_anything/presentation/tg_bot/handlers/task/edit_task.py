from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from learn_anything.presentors.tg_bot.keyboards.task.edit_task import get_task_edit_menu_kb
from learn_anything.presentors.tg_bot.texts.get_task import get_task_text

router = Router()


@router.callback_query(F.data.startswith('edit_task-'))
async def get_task_edit_menu(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    course_id, back_to = data['course_id'], data['back_to']

    tasks = data[f'course_{course_id}_tasks']
    target_task = tasks[data[f'course_{course_id}_tasks_pointer']]

    text = get_task_text(target_task)

    if callback_query.message.text:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=text,
            reply_markup=get_task_edit_menu_kb(
                task=target_task,
                course_id=course_id,
                back_to=back_to,
            ),
        )
    else:
        await bot.edit_message_caption(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            caption=text,
            reply_markup=get_task_edit_menu_kb(
                task=target_task,
                course_id=course_id,
                back_to=back_to,
            ),
        )
