from datetime import datetime
from typing import Sequence
from dataclasses import dataclass

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import \
    RegistrationForCourseGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway, GetTasksFilters
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.models import TaskID


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
    # creator: str
    created_at: datetime


@dataclass
class GetCourseTasksOutputData:
    tasks: Sequence[TaskData]
    pagination: Pagination
    total: int


class GetCourseTasksInteractor:
    def __init__(
            self,
            task_gateway: TaskGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            id_provider: IdentityProvider
    ) -> None:
        self._task_gateway = task_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._id_provider = id_provider

    async def execute(self, data: GetCourseTasksInputData) -> GetCourseTasksOutputData:
        tasks, total = await self._task_gateway.with_course(
            course_id=data.course_id,
            pagination=data.pagination,
            filters=data.filters,
        )
        print('Loaded course tasks:', tasks)

        tasks_output_data = []
        for task in tasks:
            # creator = await self._user_gateway.with_id(task.creator_id)
            tasks_output_data.append(
                TaskData(
                    id=task.id,
                    title=task.title,
                    body=task.body,
                    created_at=task.created_at,
                    # creator=creator.fullname,
                )
            )

        return GetCourseTasksOutputData(
            tasks=tasks_output_data,
            pagination=data.pagination,
            total=total,
        )


