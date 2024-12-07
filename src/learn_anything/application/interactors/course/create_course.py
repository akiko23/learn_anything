from dataclasses import dataclass
from typing import BinaryIO

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.file_manager import FileManager, COURSES_DEFAULT_DIRECTORY
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.domain.entities.course.models import CourseID
from learn_anything.domain.entities.course.rules import create_course


@dataclass
class CreateCourseInputData:
    title: str
    description: str
    photo_id: str | None
    photo: BinaryIO | None
    registrations_limit: int | None


@dataclass
class CreateCourseOutputData:
    id: CourseID


class CreateCourseInteractor:
    def __init__(self, course_gateway: CourseGateway, user_gateway: UserGateway, id_provider: IdentityProvider,
                 file_manager: FileManager, commiter: Commiter) -> None:
        self._course_gateway = course_gateway
        self._user_gateway = user_gateway
        self._commiter = commiter
        self._id_provider = id_provider
        self._file_manager = file_manager

    async def execute(self, data: CreateCourseInputData) -> CreateCourseOutputData:
        actor_id = await self._id_provider.get_current_user_id()
        if data.photo:
            file_path = await self._file_manager.generate_path(
                directories=(COURSES_DEFAULT_DIRECTORY,),
                filename=data.photo_id,
            )
            await self._file_manager.save(data.photo.read(), file_path=file_path)

        course = create_course(
            id_=None,
            title=data.title,
            description=data.description,
            creator_id=actor_id,
            is_published=False,
            photo_id=data.photo_id,
            registrations_limit=None
        )
        new_course_id = await self._course_gateway.save(course=course)

        await self._commiter.commit()

        return CreateCourseOutputData(id=new_course_id)
