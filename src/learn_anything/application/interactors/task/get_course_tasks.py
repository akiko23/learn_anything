from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import \
    CourseGateway
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway, GetTasksFilters
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_read_access
from learn_anything.entities.task.enums import TaskType
from learn_anything.entities.task.models import TaskID, CodeTask, CodeTaskTestID
from learn_anything.entities.task.rules import is_task_solved_by_actor


@dataclass
class GetCourseTasksInputData:
    course_id: CourseID
    pagination: Pagination
    filters: GetTasksFilters | None = None


@dataclass
class CodeTaskTestData:
    id: CodeTaskTestID
    code: str


@dataclass
class TaskData:
    id: TaskID
    title: str
    body: str
    topic: str | None
    type: TaskType
    # creator: str
    created_at: datetime
    updated_at: datetime

    # any practice task fields
    total_submissions: int | None = None
    total_correct_submissions: int | None = None
    solved_by_actor: bool | None = None
    attempts_limit: int | None = None
    total_actor_submissions: int | None = None

    # code task fields
    code_duration_timeout: int | None = None
    tests: Sequence[CodeTaskTestData] | None = None


@dataclass
class GetCourseTasksOutputData:
    tasks: Sequence[TaskData]
    pagination: Pagination
    total: int


class GetCourseTasksInteractor:
    def __init__(
            self,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            submission_gateway: SubmissionGateway,
            user_gateway: UserGateway,
            id_provider: IdentityProvider
    ) -> None:
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._submission_gateway = submission_gateway
        self._user_gateway = user_gateway
        self._id_provider = id_provider

    async def execute(self, data: GetCourseTasksInputData) -> GetCourseTasksOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(data.course_id)
        share_rules = await self._course_gateway.get_share_rules(data.course_id)

        ensure_actor_has_read_access(actor_id=actor_id, course=course, share_rules=share_rules)

        tasks, total = await self._task_gateway.with_course(
            course_id=data.course_id,
            pagination=data.pagination,
            filters=data.filters,
        )

        tasks_output_data = []
        for task in tasks:
            # creator = await self._user_gateway.with_id(task.creator_id)

            task_data = TaskData(
                id=task.id,
                title=task.title,
                body=task.body,
                topic=task.topic,
                type=task.type,
                created_at=task.created_at,
                # creator=creator.fullname,
                updated_at=course.updated_at,
            )

            if task.type == TaskType.CODE:
                task: CodeTask = await self._task_gateway.get_code_task_with_id(task_id=task.id)

                total_submissions = await self._submission_gateway.total_with_task_id(task_id=task.id)
                total_correct_submissions = await self._submission_gateway.total_correct_with_task_id(task_id=task.id)

                user_submissions = await self._submission_gateway.with_id(
                    user_id=actor_id, task_id=task.id
                )

                task_data.attempts_limit = task.attempts_limit
                task_data.total_actor_submissions = len(user_submissions)
                task_data.total_submissions = total_submissions
                task_data.total_correct_submissions = total_correct_submissions
                task_data.solved_by_actor = is_task_solved_by_actor(actor_submissions=user_submissions)
                task_data.code_duration_timeout = task.code_duration_timeout

                task_data.tests = [
                    CodeTaskTestData(
                        id=test.id,
                        code=test.code
                    )
                    for test in task.tests
                ]

            tasks_output_data.append(task_data)

        return GetCourseTasksOutputData(
            tasks=tasks_output_data,
            pagination=data.pagination,
            total=total,
        )
