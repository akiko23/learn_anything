import io
from dataclasses import dataclass
from typing import Any

from aiogram.types import InlineKeyboardMarkup

from learn_anything.application.interactors.course.update_course import UpdateCourseInteractor


@dataclass
class NoMediaOnTelegramServersException(Exception):
    media_path: str
    text_to_send: str
    keyboard: InlineKeyboardMarkup
    update_interactor: UpdateCourseInteractor
    interactor_input_data: Any
