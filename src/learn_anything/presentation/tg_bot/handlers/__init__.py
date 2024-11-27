from aiogram import Dispatcher
from aiogram import F
from aiogram.filters import ExceptionTypeFilter

from learn_anything.entities.error import ApplicationError
from .auth_link import router as auth_link_router
from .course.create_course import router as create_course_router
from .course.delete_course import router as delete_course_router
from .course.edit_course import router as edit_course_router
from .course.get_all_courses import router as get_all_courses_router
from .course.get_course import router as get_course_router
from .course.get_courses_actor_created import router as get_courses_actor_created_router
from .course.get_courses_actor_registered_in import router as get_courses_actor_registered_router
from .course.leave_course import router as leave_course_router
from .course.publish_course import router as publish_course_router
from .course.register_for_course import router as register_for_course_router
from .exception_handlers import handle_user_error, exception_handler, load_media_if_not_exists
from .start import router as start_router
from .submission.process_task_submission import router as process_task_submission_router
from .task.create_task import router as create_course_task_router
from .task.do_couse_task import router as do_course_task_router
from .task.edit_task import router as edit_task_router
from .task.edit_code_task import router as edit_code_task_router
from .task.delete_task import router as delete_task_router
from .task.get_course_tasks import router as get_course_tasks_router
from ..exceptions import NoMediaOnTelegramServersException


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(auth_link_router)

    dp.include_router(get_all_courses_router)
    dp.include_router(create_course_router)
    dp.include_router(get_courses_actor_created_router)
    dp.include_router(get_courses_actor_registered_router)
    dp.include_router(get_course_router)
    dp.include_router(register_for_course_router)
    dp.include_router(leave_course_router)
    dp.include_router(edit_course_router)
    dp.include_router(publish_course_router)
    dp.include_router(delete_course_router)

    dp.include_router(get_course_tasks_router)
    dp.include_router(do_course_task_router)
    dp.include_router(create_course_task_router)
    dp.include_router(edit_task_router)
    dp.include_router(edit_code_task_router)
    dp.include_router(delete_task_router)

    dp.include_router(process_task_submission_router)

    # register global error handler
    dp.error.register(
        handle_user_error,
        ExceptionTypeFilter(ApplicationError),
        (F.update.message.as_("msg") | F.update.callback_query.message.as_("msg"))
    )
    dp.error.register(
        load_media_if_not_exists,
        ExceptionTypeFilter(NoMediaOnTelegramServersException),
        (F.update.message.as_("msg") | F.update.callback_query.message.as_("msg"))
    )
    dp.error.register(
        exception_handler
    )

