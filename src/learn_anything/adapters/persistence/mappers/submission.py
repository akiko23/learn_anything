from typing import Sequence

from sqlalchemy import select, func, and_, insert
from sqlalchemy.ext.asyncio import AsyncSession

from learn_anything.adapters.persistence.tables.submission import submissions_table
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.entities.submission.models import Submission, CodeSubmission, PollSubmission, TextInputSubmission
from learn_anything.entities.task.models import TaskID
from learn_anything.entities.user.models import UserID


class SubmissionMapper(SubmissionGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def with_user_id(self, user_id: UserID) -> Submission:
        stmt = select(Submission).where(submissions_table.c.user_id == user_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def with_user_and_task_id(self, user_id: UserID, task_id: TaskID) -> Sequence[Submission]:
        stmt = (
            select(Submission).
            where(submissions_table.c.user_id == user_id).
            where(submissions_table.c.task_id == task_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def total_with_task_id(self, task_id: TaskID) -> int:
        stmt = (
            select(
                func.count()
            ).
            where(submissions_table.c.task_id == task_id)
        )
        result = await self._session.execute(stmt)

        return result.scalar_one()

    async def total_correct_with_task_id(self, task_id: TaskID) -> int:
        stmt = (
            select(
                func.count()
            ).
            where(submissions_table.c.task_id == task_id).
            where(submissions_table.c.is_correct)
        )
        result = await self._session.execute(stmt)

        return result.scalar_one()

    async def save_for_code_task(self, submission: CodeSubmission) -> None:
        stmt = (
            insert(submissions_table).
            values(
                user_id=submission.user_id,
                task_id=submission.task_id,
                is_correct=submission.is_correct,
                code=submission.code,
            )
        )

        await self._session.execute(stmt)

    async def save_for_poll_task(self, submission: PollSubmission) -> None:
        raise NotImplementedError

    async def save_for_text_input_task(self, submission: TextInputSubmission) -> None:
        raise NotImplementedError

    async def get_user_submissions_number_for_task(self, user_id: UserID, task_id: TaskID) -> int:
        stmt = (
            select(func.count()).
            where(
                and_(
                    submissions_table.c.user_id == user_id,
                    submissions_table.c.task_id == task_id,
                )
            )
        )

        res = await self._session.execute(stmt)
        return res.scalar_one()
