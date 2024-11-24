from aiogram.fsm.state import StatesGroup, State


class SearchAllBy(StatesGroup):
    author = State()
    title = State()


class SearchCreatedBy(StatesGroup):
    title = State()


class SearchRegisteredBy(StatesGroup):
    title = State()


class CreateCourse(StatesGroup):
    get_title = State()
    get_description = State()
    get_photo = State()
    get_registrations_limit = State()


class EditCourseForm(StatesGroup):
    get_title = State()
    get_description = State()
