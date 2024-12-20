from dataclasses import dataclass
from datetime import datetime
from typing import Sequence, TypeAlias

from learn_anything.course_platform.application.input_data import Pagination
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.data.course_gateway import \
    CourseGateway
from learn_anything.course_platform.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.course_platform.application.ports.data.task_gateway import TaskGateway, GetTasksFilters
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.domain.entities.course.rules import ensure_actor_has_read_access, \
    actor_has_write_access
from learn_anything.course_platform.domain.entities.task.enums import TaskType
from learn_anything.course_platform.domain.entities.task.models import TaskID, CodeTask
from learn_anything.course_platform.domain.entities.task.rules import is_task_solved_by_actor


@dataclass
class GetCourseTasksInputData:
    course_id: CourseID
    pagination: Pagination
    filters: GetTasksFilters | None = None


@dataclass
class BaseTaskData:
    id: TaskID
    title: str
    body: str
    topic: str | None
    type: TaskType
    # creator: str
    created_at: datetime
    updated_at: datetime
    actor_has_write_access: bool


@dataclass
class TheoryTaskData(BaseTaskData):
    pass


@dataclass
class PracticeTaskData(BaseTaskData):
    total_submissions: int
    total_correct_submissions: int
    solved_by_actor: bool
    total_actor_submissions: int
    attempts_limit: int | None = None


@dataclass
class CodeTaskTestData:
    code: str


@dataclass(kw_only=True)
class CodeTaskData(PracticeTaskData):
    prepared_code: str | None = None
    code_duration_timeout: int
    tests: list[CodeTaskTestData]


AnyTaskData: TypeAlias = TheoryTaskData | CodeTaskData


@dataclass
class GetCourseTasksOutputData:
    tasks: Sequence[AnyTaskData]
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

            base_task_data = BaseTaskData(
                id=task.id,
                title=task.title,
                body=task.body,
                topic=task.topic,
                type=task.type,
                created_at=task.created_at,
                # creator=creator.fullname,
                updated_at=task.updated_at,
                actor_has_write_access=actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)
            )

            task_data: TheoryTaskData | CodeTaskData
            if task.type == TaskType.THEORY:
                task_data = TheoryTaskData(
                    id=base_task_data.id,
                    title=base_task_data.title,
                    body=base_task_data.body,
                    topic=base_task_data.topic,
                    type=base_task_data.type,
                    created_at=base_task_data.created_at,
                    # creator=base_task_data.creator,
                    updated_at=base_task_data.updated_at,
                    actor_has_write_access=base_task_data.actor_has_write_access,
                )

            elif task.type == TaskType.CODE:
                code_task: CodeTask = await self._task_gateway.get_code_task_with_id(
                    task_id=task.id
                )  # type:ignore[assignment]

                total_submissions = await self._submission_gateway.total_with_task_id(task_id=code_task.id)
                total_correct_submissions = await self._submission_gateway.total_correct_with_task_id(
                    task_id=code_task.id
                )

                user_submissions = await self._submission_gateway.with_id(
                    user_id=actor_id,
                    task_id=code_task.id,
                )
                task_data = CodeTaskData(
                    id=base_task_data.id,
                    title=base_task_data.title,
                    body=base_task_data.body,
                    topic=base_task_data.topic,
                    type=base_task_data.type,
                    created_at=base_task_data.created_at,
                    # creator=base_task_data.creator,
                    updated_at=base_task_data.updated_at,
                    actor_has_write_access=base_task_data.actor_has_write_access,
                    attempts_limit=code_task.attempts_limit,
                    total_actor_submissions=len(user_submissions),
                    total_submissions=total_submissions,
                    total_correct_submissions=total_correct_submissions,
                    solved_by_actor=is_task_solved_by_actor(actor_submissions=user_submissions),
                    code_duration_timeout=code_task.code_duration_timeout,
                    prepared_code=code_task.prepared_code,
                    tests=[
                        CodeTaskTestData(
                            code=test.code
                        )
                        for test in code_task.tests
                    ]
                )
            else:
                task_data = TheoryTaskData(
                    id=base_task_data.id,
                    title=base_task_data.title,
                    body=base_task_data.body,
                    topic=base_task_data.topic,
                    type=base_task_data.type,
                    created_at=base_task_data.created_at,
                    # creator=base_task_data.creator,
                    updated_at=base_task_data.updated_at,
                    actor_has_write_access=base_task_data.actor_has_write_access,
                )

            tasks_output_data.append(task_data)

        return GetCourseTasksOutputData(
            tasks=tasks_output_data,
            pagination=data.pagination,
            total=total,
        )
