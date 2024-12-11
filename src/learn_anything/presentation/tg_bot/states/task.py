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



class EditTaskForm(StatesGroup):
    get_new_title = State()
    get_new_topic = State()
    get_new_body = State()


class EditCodeTaskForm(StatesGroup):
    get_new_prepared_code = State()
    get_new_timeout = State()
    get_new_attempts_limit = State()
    get_new_test_code = State()
    add_new_test = State()

