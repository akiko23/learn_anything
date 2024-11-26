from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.application.interactors.task.update_task import UpdateCodeTaskInputData, \
    UpdateCodeTaskInteractor
from learn_anything.entities.task.models import TaskID
from learn_anything.presentation.tg_bot.states.task import EditCodeTaskForm
from learn_anything.presentors.tg_bot.keyboards.task.edit_task import CANCEL_EDITING_KB, \
    get_task_after_edit_menu_kb

router = Router()


@router.callback_query(F.data.startswith('edit_task_timeout'))
async def start_editing_task_code_duration_timeout(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await callback_query.answer()

    await state.set_state(state=EditCodeTaskForm.get_new_timeout)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новый таймаут в секундах (не превышающий 100)',
                                 reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(EditCodeTaskForm.get_new_timeout),
    (F.text.isdigit()) & (F.text.cast(int) > 0) & (F.text.cast(int) <= 100)
)
async def edit_task_code_duration_timeout(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCodeTaskInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']
    new_timeout = int(msg.text)

    await interactor.execute(
        data=UpdateCodeTaskInputData(
            task_id=TaskID(int(task_id)),
            code_duration_timeout=new_timeout
        )
    )
    await state.set_state(state=None)

    tasks = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].code_duration_timeout = new_timeout

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Таймаут успешно обновлен',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


@router.message(StateFilter(EditCodeTaskForm.get_new_timeout))
async def handle_wrong_timeout_entry(
        msg: Message,
):
    await msg.answer('Неверный тип. Ожидалось число от 0 до 100')


@router.callback_query(F.data.startswith('edit_task_prepared_code'))
async def start_editing_task_prepared_code(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await callback_query.answer()

    await state.set_state(state=EditCodeTaskForm.get_new_timeout)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новый код инициализации задания',
                                 reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(EditCodeTaskForm.get_new_prepared_code),
    F.text.as_("new_code")
)
async def edit_task_prepared_code(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCodeTaskInteractor],
        new_code: str,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']

    await interactor.execute(
        data=UpdateCodeTaskInputData(
            task_id=TaskID(int(task_id)),
            prepared_code=new_code
        )
    )
    await state.set_state(state=None)

    tasks = data[f'course_{course_id}_tasks']
    tasks[data[f'course_{course_id}_tasks_pointer']].prepared_code = new_code

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Код инициализации успешно обновлен',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )
