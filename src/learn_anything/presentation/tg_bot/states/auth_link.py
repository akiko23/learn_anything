from aiogram.fsm.state import StatesGroup, State


class CreateAuthLinkForm(StatesGroup):
    get_role = State()
    get_usages = State()
    get_expires_at = State()
