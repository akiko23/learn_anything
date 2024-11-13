from typing import Any

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from learn_anything.application.interactors.course.get_course import GetCourseInteractor, GetCourseInputData
from learn_anything.entities.course.models import CourseID
from learn_anything.presentation.bot.keyboards.many_courses import get_all_courses_keyboard, \
    get_actor_registered_courses_keyboard, get_actor_created_courses_keyboard
from learn_anything.presentation.bot.keyboards.get_course import get_course_kb

router = Router()


@router.callback_query(F.data.startswith('course-'))
async def get_single_course(
        callback_query: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        interactor: FromDishka[GetCourseInteractor]
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

    courses = data[back_to]
    courses[data[f'{back_to}_pointer']] = target_course

    await state.update_data(
        **{back_to: courses}
    )

    if target_course.photo_id:
        await bot.send_photo(
            chat_id=user_id,
            photo=target_course.photo_id,
            caption=f"""Название: {target_course.title}

Описание: {target_course.description}

Автор: {target_course.creator.title()}

Создан: {target_course.created_at}
""",
            reply_markup=get_course_kb(
                course_id=int(course_id),
                output_data=target_course,
                back_to=back_to
            )
        )
        return

    await bot.send_message(
        chat_id=user_id,
        text=f"""Название: {target_course.title}

Описание: {target_course.description}

Автор: {target_course.creator.title()}

Создан: {target_course.created_at}
""",
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

    courses = data['courses']
    pointer = data['pointer']
    total = data['total']

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
        ),
    )
