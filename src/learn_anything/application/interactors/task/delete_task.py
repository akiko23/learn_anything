from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.domain.course.rules import ensure_actor_has_write_access
from learn_anything.domain.task.errors import TaskDoesNotExistError
from learn_anything.domain.task.models import TaskID


@dataclass
class DeleteTaskInputData:
    task_id: TaskID


class DeleteTaskInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            task_gateway: TaskGateway,
            file_manager: FileManager,
            commiter: Commiter,
            id_provider: IdentityProvider
    ) -> None:
        self._id_provider = id_provider
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._file_manager = file_manager
        self._commiter = commiter

    async def execute(self, data: DeleteTaskInputData) -> None:
        actor_id = await self._id_provider.get_current_user_id()

        task = await self._task_gateway.with_id(task_id=data.task_id)
        if not task:
            raise TaskDoesNotExistError(data.task_id)

        course = await self._course_gateway.with_id(course_id=task.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        await self._task_gateway.delete(task_id=task.id)

        await self._commiter.commit()
