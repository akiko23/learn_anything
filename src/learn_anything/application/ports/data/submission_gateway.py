from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Protocol, Sequence

from learn_anything.application.input_data import Pagination
from learn_anything.entities.submission.models import PollSubmission, CodeSubmission, TextInputSubmission, Submission
from learn_anything.entities.task.models import TaskID
from learn_anything.entities.user.models import UserID


class SortBy(StrEnum):
    DATE = auto()


@dataclass
class GetManySubmissionsFilters:
    ### public filters
    sort_by: SortBy = SortBy.DATE
    ###

    # if you want to get only submission which certain actor has created
    with_actor_id: UserID | None = None


class SubmissionGateway(Protocol):
    async def with_user_and_task_id(self, user_id: UserID, task_id: TaskID) -> Sequence[Submission]:
        raise NotImplementedError

    async def many_with_code_task_id(
            self,
            task_id: TaskID,
            filters: GetManySubmissionsFilters,
            pagination: Pagination | None = None
    ) -> (Sequence[CodeSubmission], int):
        raise NotImplementedError

    async def many_with_poll_task_id(
            self,
            task_id: TaskID,
            filters: GetManySubmissionsFilters,
            pagination: Pagination | None = None
    ) -> (Sequence[PollSubmission], int):
        raise NotImplementedError

    async def total_with_task_id(self, task_id: TaskID) -> int:
        raise NotImplementedError

    async def total_correct_with_task_id(self, task_id: TaskID) -> int:
        raise NotImplementedError

    async def save_for_code_task(self, submission: CodeSubmission) -> None:
        raise NotImplementedError

    async def save_for_poll_task(self, submission: PollSubmission) -> None:
        raise NotImplementedError

    async def save_for_text_input_task(self, submission: TextInputSubmission) -> None:
        raise NotImplementedError

    async def get_user_submissions_number_for_task(self, user_id: UserID, task_id: TaskID) -> int:
        raise NotImplementedError
