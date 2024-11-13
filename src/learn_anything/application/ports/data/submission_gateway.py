from typing import Protocol

from learn_anything.entities.submission.models import PollSubmission, CodeSubmission, Submission, TextInputSubmission
from learn_anything.entities.task.models import TaskID
from learn_anything.entities.user.models import UserID


class SubmissionGateway(Protocol):
    async def with_user_id(self, user_id: UserID) -> Submission:
        raise NotImplementedError

    async def save_for_code_task(self, submission: CodeSubmission) -> None:
        raise NotImplementedError

    async def save_for_poll_task(self, submission: PollSubmission) -> None:
        raise NotImplementedError

    async def save_for_text_input_task(self, submission: TextInputSubmission) -> None:
        raise NotImplementedError

    async def get_user_submissions_number_for_task(self, user_id: UserID, task_id: TaskID) -> int:
        raise NotImplementedError

