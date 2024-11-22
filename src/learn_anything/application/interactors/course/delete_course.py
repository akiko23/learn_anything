from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.entities.course.errors import CourseDoesNotExistError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_write_access


@dataclass
class DeleteCourseInputData:
    course_id: CourseID


class DeleteCourseInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            commiter: Commiter,
            id_provider: IdentityProvider
    ) -> None:
        self._id_provider = id_provider
        self._course_gateway = course_gateway
        self._commiter = commiter

    async def execute(self, data: DeleteCourseInputData) -> None:
        actor = await self._id_provider.get_user()
        course = await self._course_gateway.with_id(course_id=data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor.id, course=course, share_rules=share_rules)

        await self._course_gateway.delete(course_id=course.id)

        await self._commiter.commit()
