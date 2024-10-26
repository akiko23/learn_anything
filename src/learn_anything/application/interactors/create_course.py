import io
from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.errors import CourseCreationForbiddenError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import create_course
from learn_anything.entities.user.errors import UserNotAuthenticatedError
from learn_anything.entities.user.models import UserRole


@dataclass
class CreateCourseInputData:
    title: str
    description: str
    photo_id: str | None
    photo: bytes


@dataclass
class CreateCourseOutputData:
    id: CourseID


class CreateCourseInteractor:
    def __init__(self, course_gateway: CourseGateway, user_gateway: UserGateway, id_provider: IdentityProvider,
                 file_manager: FileManager) -> None:
        self._course_gateway = course_gateway
        self._user_gateway = user_gateway
        self._id_provider = id_provider
        self._file_manager = file_manager

    async def execute(self, data: CreateCourseInputData) -> CreateCourseOutputData:
        actor = await self._id_provider.get_user()
        if not actor:
            raise UserNotAuthenticatedError

        if actor.role != UserRole.TEACHER:
            raise CourseCreationForbiddenError(actor.role)

        photo_path = self._file_manager.save(data.photo, data.photo_id)
        course = create_course(
            id_=None,
            title=data.title,
            description=data.description,
            creator_id=actor.id,
            is_published=False,
            photo_path=photo_path
        )

        new_course_id = await self._course_gateway.save(course=course)
        return CreateCourseOutputData(id=new_course_id)
