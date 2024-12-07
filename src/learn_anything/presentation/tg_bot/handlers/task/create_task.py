import logging
from contextlib import suppress
from typing import Any
from typing import cast

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import ExceptionTypeFilter
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message, ErrorEvent
from dishka import FromDishka

from learn_anything.application.input_data import Pagination
from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.application.interactors.task.create_task import CreateTaskInteractor, CreateTaskInputData, \
    CreateCodeTaskInteractor, CreateCodeTaskInputData
from learn_anything.application.interactors.task.get_course_tasks import GetCourseTasksInteractor, \
    GetCourseTasksInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.enums import TaskType
from learn_anything.entities.task.errors import TaskPreparedCodeIsInvalidError, TaskTestCodeIsInvalidError, \
    InvalidTaskCodeError
from learn_anything.presentation.tg_bot.states.task import CreateTaskForm, CreateCodeTaskForm, CreateTextInputTaskForm
from learn_anything.presentors.tg_bot.keyboards.course.edit_course import get_course_edit_menu_kb
from learn_anything.presentors.tg_bot.keyboards.task.create_task import get_course_task_type_kb, \
    cancel_course_task_creation_kb, after_course_task_creation_menu, get_course_task_attempts_limit_kb, \
    get_code_task_tests_kb, get_code_duration_timeout_kb, get_code_task_prepared_code_kb, get_course_task_topic_kb
from learn_anything.presentors.tg_bot.templates import python_code_tm, pre_tm

router = Router()

logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith('create_course_task-'))
async def start_course_task_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id

    back_to, course_id = callback_query.data.split('-')[1:]

    await state.set_state(CreateTaskForm.get_title)
    await state.update_data(
        back_to=back_to,
        course_id=course_id,
    )

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите название задания',
        reply_markup=cancel_course_task_creation_kb()
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateTaskForm.get_title))
async def get_course_task_title(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        title=msg.text
    )

    await state.set_state(CreateTaskForm.get_body)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите описание задания',
        reply_markup=cancel_course_task_creation_kb(),
    )
    await state.update_data(
        msg_on_delete=msg.message_id,
    )


@router.message(StateFilter(CreateTaskForm.get_body))
async def get_course_task_description(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        body=msg.text
    )

    await state.set_state(CreateTaskForm.get_topic)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Укажите тему задания',
        reply_markup=get_course_task_topic_kb(),
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateTaskForm.get_topic))
@router.callback_query(
    StateFilter(CreateTaskForm.get_topic),
    F.data == 'create_course_task_skip_topic'
)
async def get_or_skip_course_task_topic(
        update: Message | CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = update.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        topic=update.text if isinstance(update, Message) else None
    )

    await state.set_state(CreateTaskForm.get_type)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Укажите тип задания',
        reply_markup=get_course_task_type_kb(),
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.callback_query(StateFilter(CreateTaskForm.get_type), F.data.startswith('create_course_task_type-'))
async def get_course_task_type(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateTaskInteractor],
        get_course_tasks_interactor: FromDishka[GetCourseTasksInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    course_id, back_to = CourseID(int(data['course_id'])), data['back_to']
    title = data['title']
    body = data['body']
    topic = data['topic']

    task_type = TaskType(callback_query.data.split('-')[1])

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    output_data = await get_course_tasks_interactor.execute(
        data=GetCourseTasksInputData(
            course_id=course_id,
            pagination=Pagination(offset=0, limit=0)
        )
    )

    index_in_course = output_data.total
    match task_type:
        case TaskType.THEORY:
            await state.set_state(state=None)

            await interactor.execute(
                CreateTaskInputData(
                    title=title,
                    body=body,
                    topic=topic,
                    task_type=TaskType.THEORY,
                    course_id=course_id,
                    index_in_course=index_in_course,
                )
            )

            del data['course_id']
            del data['msg_on_delete']
            with suppress(KeyError):
                del (
                    data['title'],
                    data['body'],
                )

            await state.set_data(data)

            await bot.send_message(
                chat_id=user_id,
                text=f'''Теоретическое задание успешно создано.
Название: {title}

Тело: {body}

Порядковый номер в курсе: {index_in_course + 1}
''',
                reply_markup=after_course_task_creation_menu(
                    course_id=course_id,
                    back_to=back_to
                )
            )
            return

        case TaskType.CODE:
            await state.set_state(CreateCodeTaskForm.get_attempts_limit)
        case TaskType.TEXT_INPUT:
            await state.set_state(CreateTextInputTaskForm.get_attempts_limit)
        case TaskType.POLL:
            pass

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите лимит на количество попыток',
        reply_markup=get_course_task_attempts_limit_kb(),
    )
    await state.update_data(
        msg_on_delete=msg.message_id,
    )


@router.message(
    StateFilter(CreateCodeTaskForm.get_attempts_limit),
    (F.text.isdigit()) & (F.text.cast(int) > 0) & (F.text.cast(int) <= 100)
)
@router.callback_query(
    StateFilter(CreateCodeTaskForm.get_attempts_limit),
    F.data == 'create_course_task_skip_attempts_limit',
)
async def get_or_skip_course_task_attempts_limit(
        update: Message | CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = update.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.update_data(
        attempts_limit=int(update.text) if isinstance(update, Message) else None,
    )

    await state.set_state(CreateCodeTaskForm.get_prepared_code)

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите код, который должен будет выполниться перед пользовательским кодом (a.k инициализация)',
        reply_markup=get_code_task_prepared_code_kb()
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(CreateCodeTaskForm.get_attempts_limit),
)
async def invalid_attempts_limit(
        msg: Message,
):
    await msg.answer('❗️Неверный формат данных. Ожидалось целое число от 1 до 100')


@router.message(
    StateFilter(CreateCodeTaskForm.get_prepared_code),
    F.text
)
@router.callback_query(
    StateFilter(CreateCodeTaskForm.get_prepared_code),
    F.data == 'create_course_task_skip_prepared_code'
)
async def get_or_skip_code_task_prepared_code(
        update: Message | CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = update.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.update_data(
        prepared_code=update.text if isinstance(update, Message) else None,
    )

    await state.set_state(CreateCodeTaskForm.get_code_duration_timeout)

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите таймаут для исполняемого кода в секундах (По умолчачнию - 10)',
        reply_markup=get_code_duration_timeout_kb()
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(CreateCodeTaskForm.get_code_duration_timeout),
    F.text,
    (F.text.isdigit()) & (F.text.cast(int) > 0) & (F.text.cast(int) <= 100)
)
@router.callback_query(
    StateFilter(CreateCodeTaskForm.get_code_duration_timeout),
    F.data == 'create_course_task_skip_code_timeout'
)
async def get_or_skip_task_code_duration_timeout(
        update: Message | CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = update.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.update_data(
        code_duration_timeout=int(update.text) if isinstance(update, Message) else 10,
        tests=[],
    )

    await state.set_state(CreateCodeTaskForm.get_tests)

    msg = await bot.send_message(
        chat_id=user_id,
        text=f'''Введите код для 1-го теста

Учтите:
  - Stdout и stderr пользовательского кода можно получить из переменных stdout и stderr соответственно
  - Для кодовой задачи должен быть по крайней мере один тест.
  - Лучше заранее протестируйте код, который скинете сюда, потому что создание задания происходит атомарно
''',
        reply_markup=get_code_task_tests_kb(current_tests=[])
    )
    await state.update_data(
        msg_on_delete=msg.message_id,
    )


@router.message(
    StateFilter(CreateCodeTaskForm.get_code_duration_timeout, CreateCodeTaskForm.get_attempts_limit),
)
async def handle_invalid_code_duration_timeout_or_attempts_limit(
        msg: Message,
):
    await msg.answer('❗️Неверный формат данных. Ожидалось целое число от 1 до 100')


@router.message(
    StateFilter(CreateCodeTaskForm.get_tests),
    F.text
)
async def get_code_task_tests(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    tests = data['tests']
    tests.append(msg.text)

    await state.update_data(
        tests=tests,
    )

    msg = await bot.send_message(
        chat_id=user_id,
        text=f'Введите код для {len(tests) + 1}-го теста\n'
             ''
             'Учтите:\n'
             ' - Stdout и stderr пользовательского кода можно получить из переменных stdout и stderr соответственно\n'
             ' - Для кодовой задачи должен быть по крайней мере один тест.\n'
             ' - Лучше заранее протестируйте код, который скинете сюда, потому что создание задания происходит атомарно\n',
        reply_markup=get_code_task_tests_kb(current_tests=tests)
    )
    await state.update_data(msg_on_delete=msg.message_id)


@router.callback_query(StateFilter(CreateCodeTaskForm.get_tests), F.data == 'create_course_task_finish')
async def finish_task_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateCodeTaskInteractor],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    course_id = data['course_id']
    back_to = data['back_to']
    title = data['title']
    body = data['body']
    topic = data['topic']
    prepared_code = data['prepared_code']
    index_in_course = int(data[f'course_{course_id}_tasks_total'])

    try:
        await interactor.execute(
            CreateCodeTaskInputData(
                course_id=CourseID(int(course_id)),
                task_type=TaskType.CODE,
                title=title,
                body=body,
                topic=topic,
                index_in_course=index_in_course,
                prepared_code=prepared_code,
                code_duration_timeout=data['code_duration_timeout'],
                attempts_limit=data['attempts_limit'],
                tests=data['tests'],
            )
        )
    except TaskTestCodeIsInvalidError as e:
        tests = []
        await state.update_data(tests=tests)

        msg = await bot.send_message(
            chat_id=user_id,
            text=f'Отловлена ошибка в коде тестов. Все тесты сброшены:\n'
                 f'\n{pre_tm.render(content=e.err)}\n'
                 f'\nПопробуйте снова\n'
                 f'Введите код для {len(tests) + 1}-го теста\n'
                 ''
                 'Учтите:\n'
                 ' - Stdout и stderr пользовательского кода можно получить из переменных stdout и stderr соответственно\n'
                 ' - Для кодовой задачи должен быть по крайней мере один тест.\n'
                 ' - Лучше заранее протестируйте код, который скинете сюда, потому что создание задания происходит атомарно\n',
            reply_markup=get_code_task_tests_kb(current_tests=tests),
            parse_mode='HTML'
        )
        return await state.update_data(
            msg_on_delete=msg.message_id
        )

    except TaskPreparedCodeIsInvalidError as e:
        await state.set_state(CreateCodeTaskForm.get_prepared_code)

        msg = await bot.send_message(
            chat_id=user_id,
            text=f'Отловлена ошибка в коде инициализации задания. Все, что вы выставили после этого, сброшено:\n'
                 f'\n{pre_tm.render(content=e.err)}\n'
                 f'\nПопробуйте снова\n',
            reply_markup=get_code_task_prepared_code_kb(),
            parse_mode='HTML'
        )
        return await state.update_data(
            msg_on_delete=msg.message_id
        )

    await state.set_state(state=None)

    del data['course_id']
    del data['msg_on_delete']

    del (
        data['title'],
        data['body'],
        data['attempts_limit'],
        data['prepared_code'],
        data['code_duration_timeout'],
        data['tests'],
    )

    await state.set_data(data)

    prepared_code = (
        f'Предварительный код: \n'
        f'{python_code_tm.render(code=prepared_code)}\n'
    ) if prepared_code else ''

    await bot.send_message(
        chat_id=user_id,
        text=f'''Практическое задание на код успешно создано.
Название: {title}

Тело: {body}
{prepared_code}
Порядковый номер в курсе: {index_in_course + 1}
''',
        reply_markup=after_course_task_creation_menu(
            course_id=course_id,
            back_to=back_to
        ),
        parse_mode='HTML'
    )


@router.callback_query(
    StateFilter(
        CreateTaskForm,
        CreateCodeTaskForm,
        CreateTextInputTaskForm,
    ),
    F.data == 'create_course_task_cancel'
)
async def cancel_course_task_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetCourseInteractor]
):
    await state.set_state(state=None)

    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = data['back_to'], data['course_id']

    del data['back_to']
    del data['course_id']
    del data['msg_on_delete']
    with suppress(KeyError):
        del (
            data['title'],
            data['body'],
            data['task_type'],
        )

    await state.set_data(data)

    course = await interactor.execute(
        GetCourseInputData(
            course_id=CourseID(int(course_id)),
        ),
    )

    await state.set_state(state=None)
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(
        chat_id=user_id,
        text=f"Создание задания отменено. Вы вернулись в панель управления курса",
        reply_markup=get_course_edit_menu_kb(
            course=course,
            back_to=back_to
        ),
    )


@router.error(
    ExceptionTypeFilter(
        TaskPreparedCodeIsInvalidError,
        TaskTestCodeIsInvalidError
    ),
    (F.update.message.as_("msg") | F.update.callback_query.message.as_("msg"))
)
async def handle_invalid_code_error(
        event: ErrorEvent, msg: Message
):
    user_id: int = msg.from_user.id
    err: InvalidTaskCodeError = cast(InvalidTaskCodeError, event.exception)

    logger.warning(
        'User with id=%d ran following code: \'%s\' and got error: \'%s\'',
        user_id,
        err.code,
        err.message
    )
    await msg.answer(err.message)
