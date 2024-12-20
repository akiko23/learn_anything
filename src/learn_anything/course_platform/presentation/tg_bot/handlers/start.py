from aiogram import Bot, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka import FromDishka

from learn_anything.course_platform.adapters.auth.errors import UserDoesNotExistError
from learn_anything.course_platform.application.interactors.auth.authenticate import AuthenticateInteractor, \
    AuthInputData, AuthOutputData
from learn_anything.course_platform.application.interactors.auth.register import RegisterInteractor, RegisterInputData, \
    RegisterOutputData
from learn_anything.course_platform.application.interactors.auth_link.login_with_auth_link import \
    LoginWithAuthLinkInteractor, \
    LoginWithAuthLinkInputData
from learn_anything.course_platform.domain.entities.user.models import UserID
from learn_anything.course_platform.presentors.tg_bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_auth_link(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        command: CommandObject,
        login_with_auth_link_interactor: FromDishka[LoginWithAuthLinkInteractor],
) -> None:
    user_id: int = msg.chat.id
    fullname: str = msg.chat.full_name
    username: str | None = msg.chat.username

    if not username:
        await msg.answer('Для корректной работы с ботом выставите юзернейм в настройках Телеграм')
        return
    if not command.args:
        return

    output_data = await login_with_auth_link_interactor.execute(
        LoginWithAuthLinkInputData(
            user_id=UserID(user_id),
            fullname=fullname,
            username=username,
            auth_token=command.args
        ),
    )
    is_newbie = output_data.is_newbie
    await state.update_data(role=output_data.role)

    if is_newbie:
        await bot.send_message(
            chat_id=user_id,
            text=f"Добро пожаловать, {fullname}. Твоя роль: {output_data.role}",
            reply_markup=get_main_menu_keyboard(user_role=output_data.role),
        )
        return
    await bot.send_message(
        chat_id=user_id,
        text=f"Привет, {fullname}. Твоя роль: {output_data.role}",
        reply_markup=get_main_menu_keyboard(user_role=output_data.role),
    )


@router.message(CommandStart(deep_link=False))
async def cmd_start_no_deep_link(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        register_interactor: FromDishka[RegisterInteractor],
        authenticate_interactor: FromDishka[AuthenticateInteractor],
) -> None:
    user_id: int = msg.chat.id
    fullname: str = msg.chat.full_name
    username: str | None = msg.chat.username

    if not username:
        await msg.answer('Для корректной работы с ботом выставите юзернейм в настройках Телеграм')
        return

    output_data: RegisterOutputData | AuthOutputData
    try:
        output_data = await authenticate_interactor.execute(data=AuthInputData(
            username=username,
            password='',
        ))
        is_newbie = False
    except UserDoesNotExistError:
        output_data = await register_interactor.execute(
            data=RegisterInputData(
                fullname=fullname,
                username=username,
                password='',
            )
        )
        is_newbie = True

    await state.update_data(role=output_data.role)

    if is_newbie:
        await bot.send_message(
            chat_id=user_id,
            text=f"Добро пожаловать, {fullname}. Твоя роль: {output_data.role}",
            reply_markup=get_main_menu_keyboard(user_role=output_data.role),
        )
        return
    await bot.send_message(
        chat_id=user_id,
        text=f"Привет, {fullname}. Твоя роль: {output_data.role}",
        reply_markup=get_main_menu_keyboard(user_role=output_data.role),
    )
