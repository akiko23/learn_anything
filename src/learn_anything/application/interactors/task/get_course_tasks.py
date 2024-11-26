from dataclasses import dataclass
from datetime import datetime
from typing import Sequence, Union

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import \
    CourseGateway
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway, GetTasksFilters
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_read_access
from learn_anything.entities.task.models import TaskID, TaskType, PracticeTask, CodeTask
from learn_anything.entities.task.rules import is_task_solved_by_actor


@dataclass
class GetCourseTasksInputData:
    course_id: CourseID
    pagination: Pagination
    filters: GetTasksFilters | None = None


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


@dataclass
class TheoryTaskData(TaskData):
    pass


@dataclass
class PracticeTaskData(TaskData):
    total_submissions: int
    total_correct_submissions: int
    solved_by_actor: bool
    attempts_left: int


@dataclass
class CodeTaskData(PracticeTaskData):
    code_duration_timeout: int


AnyTaskData = Union[TheoryTaskData | PracticeTaskData]


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
        actor = await self._id_provider.get_user()

        course = await self._course_gateway.with_id(data.course_id)
        share_rules = await self._course_gateway.get_share_rules(data.course_id)

        ensure_actor_has_read_access(actor_id=actor.id, course=course, share_rules=share_rules)

        tasks, total = await self._task_gateway.with_course(
            course_id=data.course_id,
            pagination=data.pagination,
            filters=data.filters,
        )
        print('Loaded course tasks:', tasks)

        tasks_output_data = []
        for task in tasks:
            # creator = await self._user_gateway.with_id(task.creator_id)

            if task.type == TaskType.THEORY:
                task_data = TheoryTaskData(
                    id=task.id,
                    title=task.title,
                    body=task.body,
                    topic=task.topic,
                    type=task.type,
                    created_at=task.created_at,
                    # creator=creator.fullname,
                    updated_at=course.updated_at,
                )

            elif task.type == TaskType.CODE:
                task: CodeTask

                total_submissions = await self._submission_gateway.total_with_task_id(task_id=task.id)
                total_correct_submissions = await self._submission_gateway.total_correct_with_task_id(task_id=task.id)

                user_submissions = await self._submission_gateway.with_user_and_task_id(
                    user_id=actor.id, task_id=task.id
                )

                is_solved: bool = is_task_solved_by_actor(actor_submissions=user_submissions)

                task_data = CodeTaskData(
                    id=task.id,
                    title=task.title,
                    body=task.body,
                    topic=task.topic,
                    type=task.type,
                    created_at=task.created_at,
                    # creator=creator.fullname,
                    total_submissions=total_submissions,
                    total_correct_submissions=total_correct_submissions,
                    solved_by_actor=is_solved,
                    code_duration_timeout=task.code_duration_timeout,
                    attempts_left=task.attempts_limit,
                    updated_at=course.updated_at,
                )

            tasks_output_data.append(task_data)

        return GetCourseTasksOutputData(
            tasks=tasks_output_data,
            pagination=data.pagination,
            total=total,
        )
