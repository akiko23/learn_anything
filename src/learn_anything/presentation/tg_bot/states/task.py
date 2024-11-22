from aiogram.fsm.state import StatesGroup, State


class CreateTask(StatesGroup):
    get_title = State()
    get_body = State()
    get_topic = State()
    get_type = State()



class CreateCodeTask(StatesGroup):
    get_attempts_limit = State()
    get_prepared_code = State()
    get_code_duration_timeout = State()
    get_tests = State()



class CreateTextInputTask(StatesGroup):
    get_attempts_limit = State()



