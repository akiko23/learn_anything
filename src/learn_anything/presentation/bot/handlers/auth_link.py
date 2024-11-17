from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.deep_linking import create_start_link

from learn_anything.application.interactors.auth.create_auth_link import CreateAuthLinkInteractor, \
    CreateAuthLinkInputData
from learn_anything.entities.user.models import UserRole
from learn_anything.presentation.bot.keyboards.create_auth_link import CANCEL_AUTH_LINK_CREATION_KB

from learn_anything.presentation.bot.keyboards.main_menu import get_main_menu_keyboard
from learn_anything.presentation.bot.states.auth_link import CreateAuthLink

router = Router()


@router.callback_query(F.data == 'main_menu-create_auth_link')
async def start_auth_link_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot
):
    user_id: int = callback_query.from_user.id

    await state.set_state(CreateAuthLink.get_role)

    msg = await bot.send_message(
        chat_id=user_id,
        text=f"Введите роль, которую получит пользователь после перехода по ссылке",
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateAuthLink.get_role))
async def get_auth_link_role(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        for_role=msg.text
    )

    await state.set_state(CreateAuthLink.get_usages)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите количество возможных использований',
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateAuthLink.get_usages))
async def get_auth_link_usages(
        msg: Message,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    await state.update_data(
        usages=msg.text
    )

    await state.set_state(CreateAuthLink.get_expires_at)
    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите дату, до которой ссылка будет валидна',
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateAuthLink.get_expires_at))
async def get_auth_link_expires_at(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateAuthLinkInteractor],
):
    await state.set_state(state=None)

    user_id: int = msg.from_user.id
    data: dict[str, Any] = await state.get_data()

    output_data = await interactor.execute(
        data=CreateAuthLinkInputData(
            for_role=data['for_role'],
            usages=data['usages'],
            expires_at=data['expires_at'],
        )
    )

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    del data['msg_on_delete']
    del data['for_role']
    del data['usages']
    del data['expires_at']

    await state.set_data(data)

    await bot.send_message(
        chat_id=user_id,
        text=f'Ссылка успешно создана: {create_start_link(bot=bot, payload=output_data.token)}',
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )


@router.callback_query(StateFilter(CreateAuthLink), F.data == 'create_auth_link-cancel')
async def cancel_auth_link_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        user_role: UserRole,
):
    user_id: int = callback_query.from_user.id

    await state.set_state(state=None)

    await bot.send_message(
        chat_id=user_id,
        text=f"Процесс создания ссылки для входа отменен",
        reply_markup=get_main_menu_keyboard(user_role=user_role),
    )
