from aiogram.fsm.state import StatesGroup, State


class CreateTaskForm(StatesGroup):
    get_title = State()
    get_body = State()
    get_topic = State()
    get_type = State()



class CreateCodeTaskForm(StatesGroup):
    get_attempts_limit = State()
    get_prepared_code = State()
    get_code_duration_timeout = State()
    get_tests = State()



class CreateTextInputTaskForm(StatesGroup):
    get_attempts_limit = State()



