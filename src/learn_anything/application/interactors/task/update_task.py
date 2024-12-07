from dataclasses import dataclass
from datetime import datetime

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.domain.entities.course.errors import CourseDoesNotExistError
from learn_anything.domain.entities.course.rules import ensure_actor_has_write_access
from learn_anything.domain.entities.task.models import TaskID


@dataclass
class UpdateTaskInputData:
    task_id: TaskID
    title: str | None = None
    topic: str | None = None
    body: str | None = None


@dataclass
class UpdateTaskOutputData:
    id: TaskID


class UpdateTaskInteractor:
    def __init__(
            self,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            user_gateway: UserGateway,
            id_provider: IdentityProvider,
            file_manager: FileManager, commiter: Commiter
    ) -> None:
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._user_gateway = user_gateway
        self._commiter = commiter
        self._id_provider = id_provider
        self._file_manager = file_manager

    async def execute(self, data: UpdateTaskInputData) -> UpdateTaskOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        task = await self._task_gateway.with_id(data.task_id)
        if not task:
            raise CourseDoesNotExistError

        course = await self._course_gateway.with_id(task.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        if data.title:
            task.title = data.title

        if data.topic:
            task.topic = data.topic

        if data.body:
            task.body = data.body

        task.updated_at = datetime.now()
        course.updated_at = datetime.now()

        updated_task_id = await self._task_gateway.save(task=task)
        await self._course_gateway.save(course=course)

        await self._commiter.commit()

        return UpdateTaskOutputData(id=updated_task_id)
