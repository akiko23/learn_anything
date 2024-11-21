from aiogram import Bot, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from aiogram.fsm.context import FSMContext

from learn_anything.application.interactors.auth.authenticate import Authenticate, AuthInputData
from learn_anything.entities.user.models import UserID

from learn_anything.presentation.tg_bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(
        msg: Message | CallbackQuery,
        state: FSMContext,
        bot: Bot,
        command: CommandObject,
        interactor: FromDishka[Authenticate],
):
    user_id: int = msg.from_user.id
    fullname: str = msg.from_user.full_name
    username: str | None = msg.from_user.username

    output_data = await interactor.execute(
        AuthInputData(
            user_id=UserID(user_id),
            fullname=fullname,
            username=username,
            token=command.args,
        ),
    )

    await state.update_data(role=output_data.role)

    if output_data.is_newbie:
        return await bot.send_message(
            chat_id=user_id,
            text=f"Добро пожаловать, {fullname}. Твоя роль: {output_data.role}",
            reply_markup=get_main_menu_keyboard(user_role=output_data.role),
        )
    await bot.send_message(
        chat_id=user_id,
        text=f"Привет, {fullname}. Твоя роль: {output_data.role}",
        reply_markup=get_main_menu_keyboard(user_role=output_data.role),
    )
