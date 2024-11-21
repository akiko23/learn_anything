from typing import Any

import aiogram.exceptions
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from aiogram.types import BufferedInputFile

from learn_anything.application.interactors.course.create_course import CreateCourseInteractor, CreateCourseInputData
from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.application.interactors.course.update_course import UpdateCourseInteractor, UpdateCourseInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.presentation.tg_bot.keyboards.course.many_courses import get_all_courses_keyboard, \
    get_actor_registered_courses_keyboard, get_actor_created_courses_keyboard
from learn_anything.presentation.tg_bot.keyboards.course.get_course import get_course_kb

router = Router()


@router.callback_query(F.data.startswith('course-'))
async def get_single_course(
        callback_query: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        interactor: FromDishka[GetCourseInteractor],
        update_course_interactor: FromDishka[UpdateCourseInteractor]
):
    user_id: int = callback_query.from_user.id
    data: dict[str, Any] = await state.get_data()

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

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

    text = f"""Название: {target_course.title}

Описание: {target_course.description}

Автор: {target_course.creator.title()}

Создан: {target_course.created_at}
"""

    if target_course.photo_id:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=target_course.photo_id,
                caption=text,
                reply_markup=get_course_kb(
                    course_id=int(course_id),
                    output_data=target_course,
                    back_to=back_to
                )
            )
        except aiogram.exceptions.TelegramBadRequest:
            msg = await bot.send_photo(
                chat_id=user_id,
                photo=BufferedInputFile(target_course.photo_reader.read(), 'stub'),
                caption=text,
                reply_markup=get_course_kb(
                    course_id=int(course_id),
                    output_data=target_course,
                    back_to=back_to
                )
            )

            new_photo_id = msg.photo[-1].file_id
            new_photo = await bot.download(new_photo_id)

            await update_course_interactor.execute(
                data=UpdateCourseInputData(
                    course_id=CourseID(int(course_id)),
                    photo_id=new_photo_id,
                    photo=new_photo
                )
            )
        return

    await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=get_course_kb(
            course_id=int(course_id),
            output_data=target_course,
            back_to=back_to
        )
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
    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Зарегестрировано: {current_course.total_registered}

Автор: {current_course.creator.title()}
Создан: {current_course.created_at}
""",
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

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    courses = data['created_courses']
    pointer = data['created_courses_pointer']
    total = data['created_courses_total']

    current_course = courses[pointer]
    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Зарегестрировано: {current_course.total_registered}

Автор: {current_course.creator.title()}
Создан: {current_course.created_at}
""",
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

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)

    courses = data['registered_courses']
    pointer = data['registered_courses_pointer']
    total = data['registered_courses_total']

    current_course = courses[pointer]
    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {current_course.title}

Описание: {current_course.description}

Зарегестрировано: {current_course.total_registered}

Автор: {current_course.creator.title()}
Создан: {current_course.created_at}
""",
        reply_markup=get_actor_registered_courses_keyboard(
            pointer=pointer,
            total=total,
            current_course_id=current_course.id,
        ),
    )
