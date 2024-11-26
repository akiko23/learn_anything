# from typing import Any
#
# from aiogram import Bot, Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.types import Message
# from dishka import FromDishka
#
# from learn_anything.application.interactors.submission.create_submission import CreateCodeTaskSubmissionInteractor
#
# router = Router()
#
#
# @router.callback_query(F.data.startswith('get_my_submissions'))
# def get_my_submissions(
#         msg: Message,
#         state: FSMContext,
#         bot: Bot,
#         interactor: FromDishka[GetManySubmissionsInteractor],
# ):
#     user_id: int = msg.from_user.id
#     data: dict[str, Any] = await state.get_data()
