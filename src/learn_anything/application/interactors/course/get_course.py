import io
import os
from datetime import datetime
from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.errors import CoursePermissionError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_write_access
from learn_anything.entities.user.models import UserID


@dataclass
class GetCourseInputData:
    course_id: CourseID


@dataclass
class GetFullCourseOutputData:
    id: CourseID
    title: str
    description: str
    photo_id: str | None
    photo_reader: io.IOBase | None
    is_published: bool
    registrations_limit: int | None
    total_registered: int
    creator_id: UserID
    creator: str
    created_at: datetime
    user_is_registered: bool
    user_has_write_access: bool


class GetCourseInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetCourseInputData) -> GetFullCourseOutputData:
        actor = await self._id_provider.get_user()

        course = await self._course_gateway.with_id(data.course_id)

        creator = await self._user_gateway.with_id(course.creator_id)
        actor_is_registered = await self._registration_for_course_gateway.exists(
            user_id=actor.id,
            course_id=course.id
        )

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)

        user_has_write_access = True
        try:
            ensure_actor_has_write_access(actor_id=actor.id, course=course, share_rules=share_rules)
        except CoursePermissionError:
            user_has_write_access = False

        output_data = GetFullCourseOutputData(
            id=course.id,
            title=course.title,
            description=course.description,
            photo_id=None,
            photo_reader=None,
            is_published=course.is_published,
            registrations_limit=course.registrations_limit,
            total_registered=course.total_registered,
            created_at=course.created_at,
            creator_id=creator.id,
            creator=creator.fullname.title(),
            user_is_registered=actor_is_registered,
            user_has_write_access=user_has_write_access,
        )

        if course.photo_id:
            output_data.photo_id = course.photo_id

            photo_reader = self._file_manager.get_by_file_path(file_path=os.path.join('courses', course.photo_id))
            output_data.photo_reader = photo_reader

        return output_data
