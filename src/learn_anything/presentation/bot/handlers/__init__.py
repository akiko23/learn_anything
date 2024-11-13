from aiogram import Dispatcher

from .start import router as start_router
from .auth_link import router as auth_link_router
from .course.get_all_courses import router as get_all_courses_router
from .course.create_course import router as create_course_router
from .course.get_courses_actor_created import router as get_courses_actor_created_router
from .course.get_courses_actor_registered_in import router as get_courses_actor_registered_router
from .course.get_course import router as get_course_router
from .course.edit_course import router as edit_course_router


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(auth_link_router)
    dp.include_router(get_all_courses_router)
    dp.include_router(create_course_router)
    dp.include_router(get_courses_actor_created_router)
    dp.include_router(get_courses_actor_registered_router)
    dp.include_router(get_course_router)
    dp.include_router(edit_course_router)
