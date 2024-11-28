from typing import Sequence

from sqlalchemy import select, func, and_, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Bundle

from learn_anything.adapters.persistence.tables import poll_task_options_table
from learn_anything.adapters.persistence.tables.submission import submissions_table
from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway, GetManySubmissionsFilters
from learn_anything.entities.submission.models import CodeSubmission, PollSubmission, TextInputSubmission, Submission
from learn_anything.entities.task.models import TaskID, PollTaskOption
from learn_anything.entities.user.models import UserID


class SubmissionMapper(SubmissionGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def with_id(self, user_id: UserID, task_id: TaskID) -> Sequence[Submission]:
        stmt = (
            select(Submission).
            where(submissions_table.c.user_id == user_id).
            where(submissions_table.c.task_id == task_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def many_with_code_task_id(
            self,
            task_id: TaskID,
            filters: GetManySubmissionsFilters,
            pagination: Pagination
    ) -> (Sequence[CodeSubmission], int):
        stmt = (
            select(CodeSubmission).
            where(
                submissions_table.c.task_id == task_id
            ).
            order_by(submissions_table.c.created_at)
        )

        if filters.with_actor_id:
            stmt = stmt.where(
                submissions_table.c.user_id == filters.with_actor_id,
            )

        total_res = await self._session.execute(
            select(func.count()).select_from(stmt)
        )

        if pagination:
            stmt = (
                stmt.
                offset(pagination.offset).
                limit(pagination.limit)
            )

        result = await self._session.execute(stmt)

        total = total_res.scalar_one()
        return result.scalars().all(), total

    async def many_with_poll_task_id(
            self,
            task_id: TaskID,
            filters: GetManySubmissionsFilters,
            pagination: Pagination
    ) -> (Sequence[PollSubmission], int):
        stmt = (
            select(
                Bundle("submission", *submissions_table.c),
                Bundle(
                    "selected_option",
                    poll_task_options_table.c.id,
                    poll_task_options_table.c.content,
                ),
            ).
            join(
                poll_task_options_table,
            ).
            where(
                submissions_table.c.task_id == task_id
            ).
            order_by(submissions_table.c.created_at)
        )

        if filters.with_actor_id:
            stmt = stmt.where(
                submissions_table.c.user_id == filters.with_actor_id,
            )

        total_res = await self._session.execute(
            select(func.count()).select_from(stmt)
        )

        if pagination:
            stmt = (
                stmt.
                offset(pagination.offset).
                limit(pagination.limit)
            )

        res = await self._session.execute(stmt)

        submissions = []
        for row in res:
            submission = row.submission._mapping  # noqa
            selected_option = row.selected_option._mapping  # noqa

            submissions.append(PollSubmission(
                user_id=submission['user_id'],
                task_id=submission['task_id'],
                is_correct=submission['is_correct'],
                created_at=submission['created_at'],
                selected_option=PollTaskOption(
                    id=selected_option['id'],
                    content=selected_option['content'],
                    is_correct=submission['is_correct']
                ),
            ))

        total = total_res.scalar_one()
        return submissions, total

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
            where(
                and_(
                    submissions_table.c.is_correct,
                    submissions_table.c.task_id == task_id
                )
            )
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
