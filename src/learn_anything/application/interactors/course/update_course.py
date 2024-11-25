from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.errors import CourseDoesNotExistError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_write_access


@dataclass
class UpdateCourseInputData:
    course_id: CourseID
    title: str | None = None
    description: str | None = None
    photo_id: str | None = None
    photo: BinaryIO | None = None
    registrations_limit: int | None = None


@dataclass
class UpdateCourseOutputData:
    id: CourseID


class UpdateCourseInteractor:
    def __init__(self, course_gateway: CourseGateway, user_gateway: UserGateway, id_provider: IdentityProvider,
                 file_manager: FileManager, commiter: Commiter) -> None:
        self._course_gateway = course_gateway
        self._user_gateway = user_gateway
        self._commiter = commiter
        self._id_provider = id_provider
        self._file_manager = file_manager

    async def execute(self, data: UpdateCourseInputData) -> UpdateCourseOutputData:
        actor = await self._id_provider.get_user()

        course = await self._course_gateway.with_id(data.course_id)
        if not course:
            raise CourseDoesNotExistError

        share_rules = await self._course_gateway.get_share_rules(course_id=data.course_id)
        ensure_actor_has_write_access(actor_id=actor.id, course=course, share_rules=share_rules)

        if data.photo:
            if course.photo_id:
                old_photo_path = f'courses/{course.photo_id}'
                self._file_manager.delete(old_photo_path)

            new_photo_path = f'courses/{data.photo_id}'
            self._file_manager.save(data.photo.read(), new_photo_path)

            course.photo_id = data.photo_id

        if data.title:
            course.title = data.title

        if data.description:
            course.description = data.description

        if data.registrations_limit:
            course.registrations_limit = data.registrations_limit

        course.updated_at = datetime.now()

        updated_course_id = await self._course_gateway.save(course=course)

        await self._commiter.commit()

        return UpdateCourseOutputData(id=updated_course_id)