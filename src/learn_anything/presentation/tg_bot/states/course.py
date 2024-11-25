from aiogram.fsm.state import StatesGroup, State


class SearchAllByForm(StatesGroup):
    author = State()
    title = State()


class SearchCreatedByForm(StatesGroup):
    title = State()


class SearchRegisteredByForm(StatesGroup):
    title = State()


class CreateCourseForm(StatesGroup):
    get_title = State()
    get_description = State()
    get_photo = State()
    get_registrations_limit = State()


class EditCourseForm(StatesGroup):
    get_title = State()
    get_description = State()
    get_photo = State()
