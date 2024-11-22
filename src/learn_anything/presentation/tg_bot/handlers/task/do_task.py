

from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.application.interactors.task.get_task import GetTaskInteractor

router = Router()


@router.callback_query(F.data.startswith('do_course_task-'))
async def do_course_task(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[GetTaskInteractor],
):
    pass




