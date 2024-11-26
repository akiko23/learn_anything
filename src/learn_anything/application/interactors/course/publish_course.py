from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.entities.course.errors import CourseDoesNotExistError, CourseAlreadyPublishedError, \
    NeedAtLeastOneTaskToPublishCourseError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_write_access


@dataclass
class PublishCourseInputData:
    course_id: CourseID


class PublishCourseInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            task_gateway: TaskGateway,
            commiter: Commiter,
            id_provider: IdentityProvider
    ) -> None:
        self._id_provider = id_provider
        self._course_gateway = course_gateway
        self._task_gateway = task_gateway
        self._commiter = commiter

    async def execute(self, data: PublishCourseInputData) -> str:
        actor_id = await self._id_provider.get_current_user_id()
        course = await self._course_gateway.with_id(course_id=data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        if course.is_published:
            raise CourseAlreadyPublishedError

        total_tasks = await self._task_gateway.total_with_course(
            course_id=data.course_id,
        )
        if total_tasks == 0:
            raise NeedAtLeastOneTaskToPublishCourseError

        course.is_published = True
        await self._course_gateway.save(course)

        await self._commiter.commit()

        return course.title
