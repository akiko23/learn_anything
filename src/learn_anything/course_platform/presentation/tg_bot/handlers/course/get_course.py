from typing import Any

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InputMediaPhoto
from dishka import FromDishka

from learn_anything.course_platform.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.course_platform.application.interactors.course.update_course import UpdateCourseInputData, UpdateCourseInteractor
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.presentation.tg_bot.exceptions import NoMediaOnTelegramServersException
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.get_course import get_course_kb
from learn_anything.course_platform.presentors.tg_bot.keyboards.course.many_courses import get_all_courses_keyboard, \
    get_actor_registered_courses_keyboard, get_actor_created_courses_keyboard
from learn_anything.course_platform.presentors.tg_bot.texts.get_course import get_single_course_text
from learn_anything.course_platform.presentors.tg_bot.texts.get_many_courses import get_many_courses_text

router = Router()


@router.callback_query(F.data.startswith('course-'))
async def get_single_course(
        callback_query: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        interactor: FromDishka[GetCourseInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor],
        file_manager: FromDishka[FileManager],
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    back_to, course_id = callback_query.data.split('-')[1:]
    target_course = await interactor.execute(
        data=GetCourseInputData(
            course_id=CourseID(int(course_id)),
        )
    )

    await state.update_data(
        **{
            f'course_{course_id}_registered': target_course.user_is_registered,
            'target_course': target_course,
        },
    )

    text = get_single_course_text(target_course)
    kb = get_course_kb(
        course_id=int(course_id),
        output_data=target_course,
        back_to=back_to
    )

    photo_path = file_manager.generate_path(('defaults',), 'course_default_img.jpg')
    _, photo_id = await file_manager.get_props_by_path(path=photo_path)
    if target_course.photo_id:
        photo_id = target_course.photo_id
        photo_path = target_course.photo_path

    try:
        return await bot.edit_message_media(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            media=InputMediaPhoto(
                media=photo_id,
                caption=text
            ),
            reply_markup=kb,
        )
    except TelegramBadRequest:
        raise NoMediaOnTelegramServersException(
            media_path=photo_path,
            text_to_send=text,
            keyboard=kb,
            update_interactor=update_course_interactor,
            interactor_input_data=UpdateCourseInputData(
                course_id=target_course.id
            ),
            collection_key=back_to,
        )


@router.callback_query(F.data == 'get_course-back_to_all_courses')
async def back_to_all_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    courses = data['all_courses']
    pointer = data['all_courses_pointer']
    total = data['all_courses_total']

    current_course = courses[pointer]
    text = get_many_courses_text(current_course)

    await bot.edit_message_caption(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        caption=text,
        reply_markup=get_all_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'get_course-back_to_created_courses')
async def back_to_created_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    courses = data['created_courses']
    pointer = data['created_courses_pointer']
    total = data['created_courses_total']

    current_course = courses[pointer]
    text = get_many_courses_text(current_course)

    await bot.edit_message_caption(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        caption=text,
        reply_markup=get_actor_created_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )


@router.callback_query(F.data == 'get_course-back_to_registered_courses')
async def back_to_registered_courses(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    courses = data['registered_courses']
    pointer = data['registered_courses_pointer']
    total = data['registered_courses_total']

    current_course = courses[pointer]
    text = get_many_courses_text(current_course)

    await bot.edit_message_caption(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        caption=text,
        reply_markup=get_actor_registered_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )
