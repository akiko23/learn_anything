import asyncio
from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.domain.course.errors import CourseDoesNotExistError, UserAlreadyRegisteredForCourseError
from learn_anything.domain.course.models import CourseID
from learn_anything.domain.course.rules import increment_course_registrations_number, create_registration_for_course


@dataclass
class RegisterForCourseInputData:
    course_id: CourseID


class RegisterForCourseInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            commiter: Commiter,
            id_provider: IdentityProvider
    ) -> None:
        self._id_provider = id_provider
        self._course_gateway = course_gateway
        self._commiter = commiter
        self._registration_for_course_gateway = registration_for_course_gateway

    async def execute(self, data: RegisterForCourseInputData) -> None:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(course_id=data.course_id)
        if (not course) or (not course.is_published):
            raise CourseDoesNotExistError(data.course_id)

        registration = await self._registration_for_course_gateway.read(user_id=actor_id, course_id=course.id)
        if registration:
            raise UserAlreadyRegisteredForCourseError(course.title)

        course = increment_course_registrations_number(course=course)
        new_registration = create_registration_for_course(user_id=actor_id, course_id=course.id)

        await asyncio.gather(
            self._course_gateway.save(course),
            self._registration_for_course_gateway.save(new_registration)
        )

        await self._commiter.commit()
