from collections.abc import Sequence
from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.application.interactors.task.get_course_tasks import TaskData
from learn_anything.application.interactors.task.update_task import UpdateTaskInteractor, UpdateTaskInputData
from learn_anything.entities.task.models import TaskID
from learn_anything.presentation.tg_bot.states.task import EditTaskForm, EditCodeTaskForm
from learn_anything.presentors.tg_bot.keyboards.task.edit_task import get_task_edit_menu_kb, CANCEL_EDITING_KB, \
    get_task_after_edit_menu_kb
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

    await state.update_data(
        back_to=back_to,
        course_id=course_id,
        task_id=target_task.id,
    )


@router.callback_query(F.data.startswith('edit_task_title'))
async def start_editing_task_title(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await callback_query.answer()

    await state.set_state(state=EditTaskForm.get_new_title)

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
):
    user_id: int = msg.from_user.id
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

    tasks: Sequence[TaskData] = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].title = value

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Заголовок успешно обновлен',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(F.data.startswith('edit_task_body'))
async def start_editing_task_body(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

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
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']
    value = msg.text

    await interactor.execute(
        data=UpdateTaskInputData(
            task_id=TaskID(int(task_id)),
            body=value
        )
    )
    await state.set_state(state=None)

    tasks: Sequence[TaskData] = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].body = value

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Описание успешно обновлено',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.callback_query(F.data.startswith('edit_task_topic'))
async def start_editing_task_topic(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await callback_query.answer()

    await state.set_state(state=EditTaskForm.get_new_topic)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новую тему', reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )

@router.message(StateFilter(EditTaskForm.get_new_topic), F.text)
async def edit_task_topic(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateTaskInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']
    value = msg.text

    await interactor.execute(
        data=UpdateTaskInputData(
            task_id=TaskID(int(task_id)),
            topic=value
        )
    )
    await state.set_state(state=None)

    tasks: Sequence[TaskData] = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].topic = value

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Тема успешно обновлена',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )

@router.callback_query(StateFilter(EditTaskForm, EditCodeTaskForm), F.data == 'cancel_task_editing')
async def cancel_task_editing(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.set_state(state=None)

    course_id, back_to = data['course_id'], data['back_to']

    await bot.send_message(
        chat_id=user_id,
        text='Вы отменили процесс изменения',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )
