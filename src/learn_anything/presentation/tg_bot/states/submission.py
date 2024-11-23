from aiogram.fsm.state import StatesGroup, State


class SubmissionForm(StatesGroup):
    get_for_code = State()
