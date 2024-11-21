

from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.application.interactors.task.get_task import GetTaskInteractor, GetTaskInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.models import TaskID
from learn_anything.presentation.bot.keyboards.course.edit_course import get_course_edit_menu_kb
from learn_anything.presentation.bot.keyboards.task.do_course_task import get_course_task_kb

router = Router()


@router.callback_query(F.data.startswith('do_course_task-'))
async def do_course_task(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetTaskInteractor],
):
    pass




