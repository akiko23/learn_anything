from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.presentation.bot.keyboards.edit_course import get_course_edit_menu_kb
from learn_anything.presentation.bot.keyboards.get_course import get_course_kb

router = Router()


@router.callback_query(F.data.startswith('edit_course-'))
async def get_course_edit_menu(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    if callback_query.message.text:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=callback_query.message.text + '\nВыберите, что хотите изменить',
            reply_markup=get_course_edit_menu_kb(
                course_id=int(course_id),
                back_to=back_to
            ),
        )
    else:
        await bot.edit_message_caption(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            caption=callback_query.message.caption + '\nВыберите, что хотите изменить',
            reply_markup=get_course_edit_menu_kb(
                course_id=int(course_id),
                back_to=back_to,
            ),
        )


@router.callback_query(F.data.startswith('edit_course_back_to-'))
async def back_from_edit_course(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]

    pointer = int(data[f'{back_to}_pointer'])
    current_course = data[back_to][pointer]

    if callback_query.message.text:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            text=callback_query.message.text.replace('\nВыберите, что хотите изменить', ''),
            reply_markup=get_course_kb(
                output_data=current_course,
                course_id=int(course_id),
                back_to=back_to
            ),
        )
    else:
        await bot.edit_message_caption(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            caption=callback_query.message.caption.replace('\nВыберите, что хотите изменить', ''),
            reply_markup=get_course_kb(
                output_data=current_course,
                course_id=int(course_id),
                back_to=back_to
            ),
        )

