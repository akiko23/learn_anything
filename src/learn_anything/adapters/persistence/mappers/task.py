import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.models import Task, TaskID, CodeTask, PollTask, PollTaskOption, CodeTaskTest
from learn_anything.adapters.persistence.tables.task import tasks_table, poll_task_options_table


class TaskMapper(TaskGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def with_id(self, task_id: TaskID) -> Task | None:
        stmt = select(Task).where(tasks_table.c.id == task_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_code_task_with_id(self, task_id: TaskID) -> CodeTask:
        stmt = select(CodeTask).where(tasks_table.c.id == task_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_poll_task_with_id(self, task_id: TaskID) -> PollTask:
        select_poll_task_stmt = (
            select(PollTask, PollTaskOption).
            join(
                target=poll_task_options_table,
                onclause=tasks_table.c.id == poll_task_options_table.c.task_id
            ).
            where(tasks_table.c.id == task_id)
        )

        poll_task_res = await self._session.execute(select_poll_task_stmt)

        poll_task = poll_task_res.scalar_one()
        print(poll_task)
        print(poll_task.options)

        return poll_task

    async def with_course(self, course_id: CourseID):
        stmt = select(Task).where(tasks_table.c.course_id == course_id)
        result = await self._session.scalars(stmt)

        return result.all()

    async def save(self, task: Task) -> TaskID:
        stmt = (
            insert(tasks_table).
            values(
                id=task.id,
                type=task.type,
                title=task.title,
                body=task.body,
                course_id=task.course_id,
                index_in_course=task.index_in_course,
            )
        )

        if task.id:
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    title=task.title,
                    body=task.body,
                    index_in_course=task.index_in_course,
                ),
                where=(tasks_table.c.id == task.id)
            )

        stmt = stmt.returning(tasks_table.c.id)

        res = await self._session.execute(stmt)
        return res.scalar_one()

    async def save_code_task(self, task: CodeTask) -> TaskID:
        upsert_code_task_stmt = (
            insert(tasks_table).
            values(
                id=task.id,
                type=task.type,
                title=task.title,
                body=task.body,
                course_id=task.course_id,
                index_in_course=task.index_in_course,
                prepared_code=task.prepared_code,
                code_duration_timeout=task.code_duration_timeout,
            )
        ).on_conflict_do_update(
            constraint='tasks_pkey',
            set_=dict(
                title=task.title,
                body=task.body,
                index_in_course=task.index_in_course,
                prepared_code=task.prepared_code,
                code_duration_timeout=task.code_duration_timeout,
            )
        ).returning(tasks_table.c.id)

        insert_code_task_tests_stmt = (
            insert(CodeTaskTest).
            values(
                [
                    {"code": test.code, "task_id": task.id}
                    for test in task.tests
                ]
            )
        )
        insert_code_task_tests_stmt.on_conflict_do_update(
            constraint='code_task_tests_pkey',
            set_=dict(code=insert_code_task_tests_stmt.excluded.code),
        )

        res, _ = await asyncio.gather(
            self._session.execute(upsert_code_task_stmt),
            self._session.execute(insert_code_task_tests_stmt),
        )
        return res.scalar_one()

    async def save_poll_task(self, task: PollTask) -> TaskID:
        task_upsert_stmt = (
            insert(tasks_table).
            values(
                id=task.id,
                type=task.type,
                title=task.title,
                body=task.body,
                course_id=task.course_id,
                index_in_course=task.index_in_course
            )
        ).on_conflict_do_update(
            constraint='tasks_pkey',
            set_=dict(
                body=task.body
            )
        ).returning(tasks_table.c.id)

        options_insert_stmt = (
            insert(poll_task_options_table).
            values([
                {'id': option.id, 'content': option.content, 'is_correct': option.is_correct}
                for option in task.options
            ])
        )

        res, _ = await asyncio.gather(
            self._session.execute(task_upsert_stmt),
            self._session.execute(options_insert_stmt)
        )
        return res.scalar_one()
