import asyncio

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.entities.submission.models import Submission, CodeSubmission, PollSubmission, TextInputSubmission
from learn_anything.entities.task.models import TaskID
from learn_anything.entities.user.models import UserID
from learn_anything.adapters.persistence.tables.submission import submissions_table


class SubmissionMapper(SubmissionGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def with_user_id(self, user_id: UserID) -> Submission:
        stmt = select(Submission).where(submissions_table.c.user_id == user_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def total_with_task_id(self, task_id: TaskID) -> int:
        stmt = (
            select(
                func.count()
            ).
            where(submissions_table.c.task_id == task_id)
        )
        print(stmt)
        result = await self._session.execute(stmt)

        return result.scalar_one()

    async def save_for_code_task(self, submission: CodeSubmission) -> None:
        raise NotImplementedError

    async def save_for_poll_task(self, submission: PollSubmission) -> None:
        raise NotImplementedError

    async def save_for_text_input_task(self, submission: TextInputSubmission) -> None:
        raise NotImplementedError
