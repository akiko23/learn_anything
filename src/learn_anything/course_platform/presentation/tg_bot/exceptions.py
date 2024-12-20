from dataclasses import dataclass
from typing import Any

from aiogram.types import InlineKeyboardMarkup

from learn_anything.course_platform.application.interactors.course.update_course import UpdateCourseInteractor
from learn_anything.course_platform.application.ports.data.file_manager import FilePath


@dataclass
class NoMediaOnTelegramServersException(Exception):
    media_path: FilePath
    text_to_send: str
    keyboard: InlineKeyboardMarkup
    update_interactor: UpdateCourseInteractor
    interactor_input_data: Any
    collection_key: str
