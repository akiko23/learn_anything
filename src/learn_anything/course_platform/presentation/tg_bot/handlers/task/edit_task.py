from collections.abc import Sequence
from datetime import datetime
from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.task.get_course_tasks import BaseTaskData
from learn_anything.course_platform.application.interactors.task.update_task import UpdateTaskInteractor, \
    UpdateTaskInputData
from learn_anything.course_platform.domain.entities.task.models import TaskID
from learn_anything.course_platform.presentation.tg_bot.states.task import EditTaskForm, EditCodeTaskForm
from learn_anything.course_platform.presentors.tg_bot.keyboards.task.edit_task import get_task_edit_menu_kb, \
    CANCEL_EDITING_KB, \
    get_task_after_edit_menu_kb
from learn_anything.course_platform.presentors.tg_bot.texts.get_task import get_task_text_on_edit

router = Router()


@router.callback_query(
    F.data.startswith('edit_task-'),
    F.message.as_('callback_query_message')
)
async def get_task_edit_menu(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    course_id, back_to = data['course_id'], data['back_to']

    tasks = data[f'course_{course_id}_tasks']
    target_task = tasks[data[f'course_{course_id}_tasks_pointer']]

    text = get_task_text_on_edit(target_task)
    if callback_query_message.text:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            text=text,
            reply_markup=get_task_edit_menu_kb(
                task=target_task,
                course_id=course_id,
                back_to=back_to,
            ),
            parse_mode='HTML'
        )
    else:
        await bot.edit_message_caption(
            chat_id=user_id,
            message_id=callback_query_message.message_id,
            caption=text,
            reply_markup=get_task_edit_menu_kb(
                task=target_task,
                course_id=course_id,
                back_to=back_to,
            ),
            parse_mode='HTML'
        )

    await state.update_data(
        back_to=back_to,
        course_id=course_id,
        task_id=target_task.id,
        target_task=target_task,
    )


@router.callback_query(
    F.data.startswith('edit_task_title'),
    F.message.as_('callback_query_message')
)
async def start_editing_task_title(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id

    await state.set_state(state=EditTaskForm.get_new_title)

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новый заголовок', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(EditTaskForm.get_new_title), F.text)
async def edit_task_title(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateTaskInteractor],
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']
    value = msg.text

    await interactor.execute(
        data=UpdateTaskInputData(
            task_id=TaskID(int(task_id)),
            title=value
        )
    )
    await state.set_state(state=None)

    tasks: Sequence[BaseTaskData] = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].title = value
    tasks[data[f'course_{course_id}_tasks_pointer']].updated_at = datetime.now()

    await state.update_data(
        {f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Заголовок успешно обновлен',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(
    F.data.startswith('edit_task_body'),
    F.message.as_('callback_query_message')
)
async def start_editing_task_body(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    await callback_query.answer()

    await state.set_state(state=EditTaskForm.get_new_body)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новое тело задания', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(EditTaskForm.get_new_body), F.text)
async def edit_task_body(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateTaskInteractor],
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']
    value = msg.text

    await interactor.execute(
        data=UpdateTaskInputData(
            task_id=TaskID(int(task_id)),
            body=value
        )
    )
    await state.set_state(state=None)

    tasks: Sequence[BaseTaskData] = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].body = value

    await state.update_data(
        {f'course_{course_id}_tasks': tasks}
    )

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await bot.send_message(
        chat_id=user_id,
        text='Описание успешно обновлено',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(
    F.data.startswith('edit_task_topic'),
    F.message.as_('callback_query_message')
)
async def start_editing_task_topic(
        callback_query: CallbackQuery,
        callback_query_message: Message,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id

    await state.set_state(state=EditTaskForm.get_new_topic)

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новую тему', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(EditTaskForm.get_new_topic),
    F.text.as_('value')
)
async def edit_task_topic(
        msg: Message,
        value: str,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateTaskInteractor],
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']

    await interactor.execute(
        data=UpdateTaskInputData(
            task_id=TaskID(int(task_id)),
            topic=value
        )
    )

    tasks: Sequence[BaseTaskData] = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].topic = value
    await state.update_data(
        {f'course_{course_id}_tasks': tasks}
    )
    await state.set_state(state=None)

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await bot.send_message(
        chat_id=user_id,
        text='Тема успешно обновлена',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(StateFilter(EditTaskForm, EditCodeTaskForm), F.data == 'cancel_task_editing')
async def cancel_task_editing(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
) -> None:
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    course_id, back_to = data['course_id'], data['back_to']

    await state.set_state(state=None)

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await bot.send_message(
        chat_id=user_id,
        text='Вы отменили процесс изменения',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )
