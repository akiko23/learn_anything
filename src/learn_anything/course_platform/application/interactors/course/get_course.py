import asyncio
from dataclasses import dataclass
from datetime import datetime

from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.course_platform.application.ports.data.file_manager import FileManager, COURSES_DEFAULT_DIRECTORY, \
    FilePath
from learn_anything.course_platform.application.ports.data.task_gateway import TaskGateway
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.domain.entities.course.errors import CourseDoesNotExistError
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.domain.entities.course.rules import actor_has_write_access, \
    ensure_actor_has_read_access


@dataclass
class GetCourseInputData:
    course_id: CourseID


@dataclass
class GetFullCourseOutputData:
    id: CourseID
    title: str
    description: str
    photo_id: str | None
    photo_path: FilePath | None
    is_published: bool
    registrations_limit: int | None
    total_tasks: int
    total_registered: int
    creator: str
    created_at: datetime
    updated_at: datetime
    user_is_registered: bool
    user_has_write_access: bool


class GetCourseInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            task_gateway: TaskGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._task_gateway = task_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetCourseInputData) -> GetFullCourseOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(data.course_id)
        if not course:
            raise CourseDoesNotExistError(course_id=data.course_id)

        creator, registration = await asyncio.gather(
            self._user_gateway.with_id(course.creator_id),
            self._registration_for_course_gateway.read(
                user_id=actor_id,
                course_id=course.id
            )
        )
        creator_name = 'undefined'
        if creator:
            creator_name = creator.fullname

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_read_access(actor_id=actor_id, course=course, share_rules=share_rules)

        total_tasks = await self._task_gateway.total_with_course(course_id=course.id)
        output_data = GetFullCourseOutputData(
            id=course.id,
            title=course.title,
            description=course.description,
            photo_id=None,
            photo_path=None,
            is_published=course.is_published,
            registrations_limit=course.registrations_limit,
            total_registered=course.total_registered,
            created_at=course.created_at,
            updated_at=course.updated_at,
            creator=creator_name,
            user_is_registered=registration is not None,
            user_has_write_access=actor_has_write_access(
                actor_id=actor_id,
                course=course,
                share_rules=share_rules
            ),
            total_tasks=total_tasks,
        )

        if course.photo_id:
            output_data.photo_id = course.photo_id
            output_data.photo_path = self._file_manager.generate_path(
                directories=(COURSES_DEFAULT_DIRECTORY,),
                filename=course.photo_id,
            )

        return output_data
