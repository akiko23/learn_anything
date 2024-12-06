from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from learn_anything.application.interactors.task.get_course_tasks import TaskData, CodeTaskTestData
from learn_anything.application.interactors.task.update_code_task import UpdateCodeTaskInputData, \
    UpdateCodeTaskInteractor, UpdateCodeTaskTestInputData, UpdateCodeTaskTestInteractor
from learn_anything.entities.task.models import TaskID
from learn_anything.presentation.tg_bot.states.task import EditCodeTaskForm
from learn_anything.presentors.tg_bot.keyboards.task.edit_task import CANCEL_EDITING_KB, \
    get_task_after_edit_menu_kb
from learn_anything.presentors.tg_bot.keyboards.task.edit_task import watch_code_task_tests_kb

router = Router()


@router.callback_query(F.data.startswith('edit_task_attempts_limit'))
async def start_editing_task_attempts_limit(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    await callback_query.answer()

    await state.set_state(state=EditCodeTaskForm.get_new_attempts_limit)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новый лимит на количество попыток (null если хотите его удалить)',
                                 reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(EditCodeTaskForm.get_new_attempts_limit),
    (F.text.isdigit()) & (F.text.cast(int) > 0) & (F.text.cast(int) <= 1000)
)
async def edit_task_attempts_limit(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCodeTaskInteractor],
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, task_id = data['course_id'], data['back_to'], data['task_id']
    new_attempts_limit = int(msg.text) if msg.text != 'null' else None

    await interactor.execute(
        data=UpdateCodeTaskInputData(
            task_id=TaskID(int(task_id)),
            attempts_limit=new_attempts_limit
        )
    )
    await state.set_state(state=None)

    tasks = data[f'course_{course_id}_tasks']
    if new_attempts_limit is not None:
        tasks[data[f'course_{course_id}_tasks_pointer']].attempts_limit = new_attempts_limit

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks}
    )

    await bot.send_message(
        chat_id=user_id,
        text='Лимит на кол-во попыток успешно обновлен',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )


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


@router.message(StateFilter(EditCodeTaskForm.get_new_timeout, EditCodeTaskForm.get_new_attempts_limit))
async def handle_wrong_timeout_or_attempts_limit_entry(
        msg: Message,
):
    await msg.answer('❗️Неверный формат данных. Ожидалось целое число от 1 до 100')


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

    await state.set_state(state=EditCodeTaskForm.get_new_prepared_code)

    msg = await bot.send_message(chat_id=user_id, text='Отправьте новый код инициализации задания (null если хотите его удалить)',
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
    new_code = None if new_code.lower() == 'null' else new_code

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


@router.callback_query(F.data.startswith('get_code_task_tests'))
async def get_code_task_tests(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    target_task: TaskData = data['target_task']
    pointer = data.get(f'code_task_{target_task.id}_tests_pointer', 0)

    await state.update_data(
        **{f'code_task_{target_task.id}_tests_pointer': pointer}
    )

    current_test: CodeTaskTestData = target_task.tests[pointer]
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=f"""
Тест #{pointer + 1}:

```python
{current_test.code}
```
""",
        reply_markup=watch_code_task_tests_kb(pointer=pointer, total=len(target_task.tests), task_id=target_task.id),
        parse_mode='markdown',
    )


@router.callback_query((F.data.startswith('code_task_tests-next')) | (F.data.startswith('code_task_tests-prev')))
async def watch_code_task_tests_prev_or_next(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    command, task_id = callback_query.data.split('-')[1:]

    pointer = data[f'code_task_{task_id}_tests_pointer']

    if command == 'next':
        pointer += 1
    else:
        pointer -= 1

    target_task = data['target_task']
    current_test: CodeTaskTestData = target_task.tests[pointer]

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        text=f"""
    Тест #{pointer + 1}:

    ```python
    {current_test.code}
    ```
    """,
        reply_markup=watch_code_task_tests_kb(pointer=pointer, total=len(target_task.tests), task_id=target_task.id),
        parse_mode='markdown',
    )

    await state.update_data(
        **{f'code_task_{target_task.id}_tests_pointer': pointer}
    )


@router.callback_query(F.data.startswith('edit_code_task_test-'))
async def start_editing_code_task_test(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    task_id = callback_query.data.split('-')[1]
    pointer = data[f'code_task_{task_id}_tests_pointer']

    await callback_query.answer()

    await state.set_state(state=EditCodeTaskForm.get_new_test_code)

    msg = await bot.send_message(chat_id=user_id, text=f'Отправьте новый код теста #{pointer + 1}',
                                 reply_markup=CANCEL_EDITING_KB)
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(EditCodeTaskForm.get_new_test_code),
    F.text.as_("new_test_code")
)
async def edit_code_task_test_code(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[UpdateCodeTaskTestInteractor],
        new_test_code: str,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id, back_to, target_task = data['course_id'], data['back_to'], data['target_task']
    pointer = data[f'code_task_{target_task.id}_tests_pointer']

    target_task: TaskData
    target_test = target_task.tests[pointer]

    output_data = await interactor.execute(
        data=UpdateCodeTaskTestInputData(
            id=target_test.id,
            task_id=target_task.id,
            code=new_test_code,
        )
    )
    await state.set_state(state=None)

    tasks = data[f'course_{course_id}_tasks']
    target_test.code = output_data.new_code
    tasks[data[f'course_{course_id}_tasks_pointer']].tests = target_task.tests

    await state.update_data(
        **{f'course_{course_id}_tasks': tasks},
        target_task=target_task,
    )

    await bot.send_message(
        chat_id=user_id,
        text=f'Код теста #{pointer + 1} успешно обновлен',
        reply_markup=get_task_after_edit_menu_kb(back_to=back_to, course_id=course_id)
    )
