from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway, GetManySubmissionsFilters
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.domain.course.rules import ensure_actor_has_write_access
from learn_anything.domain.submission.models import CodeSubmission, PollSubmission
from learn_anything.domain.task.enums import TaskType
from learn_anything.domain.task.errors import TaskDoesNotExistError, TheoryTaskHasNoSubmissionsError
from learn_anything.domain.task.models import TaskID



@dataclass
class GetManySubmissionsInputData:
    task_id: TaskID
    filters: GetManySubmissionsFilters
    pagination: Pagination


@dataclass
class SubmissionData:
    solution: str
    is_correct: bool
    created_at: datetime


@dataclass
class GetManySubmissionsOutputData:
    submissions: Sequence[SubmissionData]
    pagination: Pagination
    total: int


class GetActorSubmissionsInteractor:
    def __init__(
            self,
            submission_gateway: SubmissionGateway,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._task_gateway = task_gateway
        self._submission_gateway = submission_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetManySubmissionsInputData) -> GetManySubmissionsOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        task = await self._task_gateway.with_id(data.task_id)
        if not task:
            raise TaskDoesNotExistError(task_id=data.task_id)

        if task.type == TaskType.THEORY:
            raise TheoryTaskHasNoSubmissionsError(task_id=task.id)

        data.filters.with_actor_id = actor_id

        submissions_output_data, total = [], 0
        match task.type:
            case TaskType.CODE:
                submissions, total = await self._submission_gateway.many_with_code_task_id(
                    task_id=task.id,
                    filters=data.filters,
                    pagination=data.pagination,
                )
                submissions: Sequence[CodeSubmission]

                for submission in submissions:
                    submission_data = SubmissionData(
                        solution=submission.code,
                        is_correct=submission.is_correct,
                        created_at=submission.created_at,
                    )

                    submissions_output_data.append(submission_data)

            case TaskType.POLL:
                submissions, total = await self._submission_gateway.many_with_poll_task_id(
                    task_id=task.id,
                    filters=data.filters,
                    pagination=data.pagination,
                )
                submissions: Sequence[PollSubmission]

                for submission in submissions:
                    submission_data = SubmissionData(
                        solution=submission.selected_option.content,
                        is_correct=submission.is_correct,
                        created_at=submission.created_at,
                    )

                    submissions_output_data.append(submission_data)

        return GetManySubmissionsOutputData(
            submissions=submissions_output_data,
            pagination=data.pagination,
            total=total,
        )


class GetTaskSubmissionsInteractor:
    def __init__(
            self,
            submission_gateway: SubmissionGateway,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._task_gateway = task_gateway
        self._submission_gateway = submission_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetManySubmissionsInputData) -> GetManySubmissionsOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        task = await self._task_gateway.with_id(data.task_id)
        if not task:
            raise TaskDoesNotExistError(task_id=data.task_id)

        if task.type == TaskType.THEORY:
            raise TheoryTaskHasNoSubmissionsError(task_id=task.id)

        course = await self._course_gateway.with_id(course_id=task.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        submissions_output_data, total = [], 0
        match task.type:
            case TaskType.CODE:
                submissions, total = await self._submission_gateway.many_with_code_task_id(
                    task_id=task.id,
                    filters=data.filters,
                    pagination=data.pagination,
                )
                submissions: Sequence[CodeSubmission]

                for submission in submissions:
                    submission_data = SubmissionData(
                        solution=submission.code,
                        is_correct=submission.is_correct,
                        created_at=submission.created_at,
                    )
                    submissions_output_data.append(submission_data)

            case TaskType.POLL:
                submissions, total = await self._submission_gateway.many_with_poll_task_id(
                    task_id=task.id,
                    filters=data.filters,
                    pagination=data.pagination,
                )
                submissions: Sequence[PollSubmission]

                for submission in submissions:
                    submission_data = SubmissionData(
                        solution=submission.selected_option.content,
                        is_correct=submission.is_correct,
                        created_at=submission.created_at,
                    )

                    submissions_output_data.append(submission_data)

        return GetManySubmissionsOutputData(
            submissions=submissions_output_data,
            pagination=data.pagination,
            total=total,
        )
