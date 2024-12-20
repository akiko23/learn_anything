from datetime import datetime
from typing import Any

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.deep_linking import create_start_link
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.auth_link.create_auth_link import CreateAuthLinkInteractor, \
    CreateAuthLinkInputData
from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.presentation.tg_bot.states.auth_link import CreateAuthLinkForm
from learn_anything.course_platform.presentors.tg_bot.keyboards.create_auth_link import CANCEL_AUTH_LINK_CREATION_KB
from learn_anything.course_platform.presentors.tg_bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.callback_query(
    F.data == 'main_menu-create_auth_link',
    F.message.as_('callback_query_message'),
    F.data.as_('callback_query_data')
)
async def start_auth_link_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        callback_query_message: Message,
        bot: Bot
) -> None:
    user_id: int = callback_query.from_user.id

    await bot.delete_message(chat_id=user_id, message_id=callback_query_message.message_id)

    await state.set_state(CreateAuthLinkForm.get_role)

    msg = await bot.send_message(
        chat_id=user_id,
        text="Введите роль, которую получит пользователь после перехода по ссылке",
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateAuthLinkForm.get_role), F.text.cast(UserRole).as_('for_role'))
async def get_auth_link_role(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        for_role: UserRole,
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.update_data(
        for_role=for_role
    )

    await state.set_state(CreateAuthLinkForm.get_usages)

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите количество возможных использований',
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(StateFilter(CreateAuthLinkForm.get_usages), F.text.cast(int).as_('usages'))
async def get_auth_link_usages(
        msg: Message,
        state: FSMContext,
        bot: Bot,
        usages: int,
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.update_data(
        usages=usages
    )

    await state.set_state(CreateAuthLinkForm.get_expires_at)

    msg = await bot.send_message(
        chat_id=user_id,
        text='Введите дату, до которой ссылка будет валидна (в формате %d-%m-%Y %H-%M)',
        reply_markup=CANCEL_AUTH_LINK_CREATION_KB,
    )
    await state.update_data(
        msg_on_delete=msg.message_id
    )


@router.message(
    StateFilter(CreateAuthLinkForm.get_expires_at),
    F.text.as_('expires_at_text')
)
async def get_auth_link_expires_at(
        msg: Message,
        expires_at_text: str,
        state: FSMContext,
        bot: Bot,
        interactor: FromDishka[CreateAuthLinkInteractor],
        user_role: UserRole,
) -> None:
    user_id: int = msg.chat.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=data['msg_on_delete'])

    await state.set_state(state=None)

    output_data = await interactor.execute(
        data=CreateAuthLinkInputData(
            for_role=data['for_role'],
            usages=data['usages'],
            expires_at=datetime.strptime(expires_at_text, '%d-%m-%Y %H-%M'),
        )
    )

    del data['msg_on_delete']
    del data['for_role']
    del data['usages']

    await state.set_data(data)

    link = await create_start_link(bot=bot, payload=output_data.token)
    await bot.send_message(
        chat_id=user_id,
        text=f'Ссылка успешно создана: {link}',
        reply_markup=get_main_menu_keyboard(user_role=user_role),
    )


@router.callback_query(StateFilter(CreateAuthLinkForm), F.data == 'create_auth_link-cancel')
async def cancel_auth_link_creation(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        user_role: UserRole,
) -> None:
    user_id: int = callback_query.from_user.id

    await state.set_state(state=None)

    await bot.send_message(
        chat_id=user_id,
        text="Процесс создания ссылки для входа отменен",
        reply_markup=get_main_menu_keyboard(user_role=user_role),
    )
