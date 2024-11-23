from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka

from learn_anything.application.interactors.submission.create_submission import CreateCodeTaskSubmissionInteractor
from learn_anything.presentation.tg_bot.states.submission import SubmissionForm

router = Router()


@router.message(StateFilter(SubmissionForm.get_for_code), F.text)
async def process_code_task_submission(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateCodeTaskSubmissionInteractor],
):
    pass
