from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.entities.course.errors import CourseDoesNotExistError, UserAlreadyRegisteredForCourseError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import increment_course_registrations_number, create_registration_for_course, \
    decrement_course_registrations_number


@dataclass
class LeaveCourseInputData:
    course_id: CourseID


class LeaveCourseInteractor:
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

    async def execute(self, data: LeaveCourseInputData) -> None:
        actor = await self._id_provider.get_user()
        course = await self._course_gateway.with_id(course_id=data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        if not course.is_published and actor.id != course.creator_id:
            raise CourseDoesNotExistError(data.course_id)

        course = decrement_course_registrations_number(course=course)

        await self._course_gateway.save(course)
        await self._registration_for_course_gateway.delete(user_id=actor.id, course_id=course.id)

        await self._commiter.commit()
