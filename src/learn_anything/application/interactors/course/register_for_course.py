import asyncio
from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.entities.course.errors import CourseDoesNotExistError, UserAlreadyRegisteredForCourseError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import increment_course_registrations_number, create_registration_for_course


@dataclass
class SignUpForCourseInputData:
    course_id: CourseID



class RegisterForCourseInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            id_provider: IdentityProvider
    ) -> None:
        self._id_provider = id_provider
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway

    async def execute(self, data: SignUpForCourseInputData) -> None:
        actor = await self._id_provider.get_user()
        course = await self._course_gateway.with_id(course_id=data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        registration_exists = await self._registration_for_course_gateway.exists(user_id=actor.id, course_id=course.id)
        if registration_exists:
           raise UserAlreadyRegisteredForCourseError(actor.id, course.id)

        course = increment_course_registrations_number(course=course)
        new_registration = create_registration_for_course(user_id=actor.id, course_id=course.id)

        await asyncio.gather(
            self._course_gateway.save(course),
            self._registration_for_course_gateway.save(new_registration),
        )
