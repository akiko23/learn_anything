from dataclasses import dataclass
from datetime import datetime


from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.errors import CourseDoesNotExistError
from learn_anything.entities.course.rules import actor_has_write_access, \
    ensure_actor_has_read_access
from learn_anything.entities.task.errors import TaskDoesNotExistError
from learn_anything.entities.task.models import TaskID


@dataclass
class GetTaskInputData:
    task_id: TaskID


@dataclass
class GetTaskOutputData:
    title: str
    description: str
    total_submissions: int
    created_at: datetime
    user_has_write_access: bool


class GetTaskInteractor:
    def __init__(
            self,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            submission_gateway: SubmissionGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._submission_gateway = submission_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetTaskInputData) -> GetTaskOutputData:
        actor = await self._id_provider.get_user()

        task = await self._task_gateway.with_id(data.task_id)
        if not task:
            raise TaskDoesNotExistError(task_id=data.task_id)

        course = await self._course_gateway.with_id(task.course_id)
        if not course:
            raise CourseDoesNotExistError(course_id=task.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_read_access(course=course, actor_id=actor.id, share_rules=share_rules)

        total_submissions = await self._submission_gateway.total_with_task_id(task_id=task.id)

        output_data = GetTaskOutputData(
            title=task.title,
            description=task.body,
            total_submissions=total_submissions,
            created_at=task.created_at,
            user_has_write_access=actor_has_write_access(
                actor_id=actor.id,
                course=course,
                share_rules=share_rules
            ),
        )

        return output_data
