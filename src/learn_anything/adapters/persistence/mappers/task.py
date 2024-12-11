from collections.abc import Sequence

from sqlalchemy import select, func, delete, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from learn_anything.adapters.persistence.tables import code_task_tests_table
from learn_anything.adapters.persistence.tables.task import tasks_table, poll_task_options_table
from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.data.task_gateway import TaskGateway, GetTasksFilters
from learn_anything.domain.entities.course.models import CourseID
from learn_anything.domain.entities.task.models import Task, TaskID, CodeTask, PollTask, PollTaskOption, CodeTaskTest


class TaskMapper(TaskGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def with_id(self, task_id: TaskID) -> Task | None:
        stmt = select(Task).where(tasks_table.c.id == task_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_code_task_with_id(self, task_id: TaskID) -> CodeTask | None:
        stmt = select(CodeTask).where(tasks_table.c.id == task_id)
        result = await self._session.execute(stmt)

        task: CodeTask | None = result.scalar_one_or_none()
        if task is None:
            return task

        get_tests_stmt = select(CodeTaskTest).where(code_task_tests_table.c.task_id == task_id).order_by(code_task_tests_table.c.index_in_task)
        get_tests_result = await self._session.execute(get_tests_stmt)

        task.tests = get_tests_result.scalars().all()
        return task

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

        return poll_task

    async def with_course(self, course_id: CourseID, pagination: Pagination, filters: GetTasksFilters | None) -> (
            Sequence[Task], int):
        stmt = (
            select(
                Task
            ).
            where(tasks_table.c.course_id == course_id).
            order_by(tasks_table.c.index_in_course)
        )

        total_res = await self._session.execute(
            select(func.count()).select_from(stmt)
        )

        stmt = (
            stmt.
            offset(pagination.offset).
            limit(pagination.limit)
        )

        result = await self._session.scalars(stmt)

        return result.all(), total_res.scalar_one()

    async def total_with_course(self, course_id: CourseID) -> int:
        stmt = (
            select(
                Task
            ).
            where(tasks_table.c.course_id == course_id)
        )

        res = await self._session.execute(
            select(func.count()).select_from(stmt)
        )
        return res.scalar_one()

    async def save(self, task: Task) -> TaskID:
        stmt = (
            insert(tasks_table).
            values(
                title=task.title,
                topic=task.topic,
                body=task.body,
                type=task.type,
                course_id=task.course_id,
                index_in_course=task.index_in_course,
            )
        )

        if task.id:
            stmt = (
                insert(tasks_table).
                values(
                    id=task.id,
                    title=task.title,
                    topic=task.topic,
                    body=task.body,
                    type=task.type,
                    course_id=task.course_id,
                    index_in_course=task.index_in_course,
                )
                .on_conflict_do_update(
                    index_elements=['id'],
                    set_=dict(
                        title=task.title,
                        topic=task.topic,
                        body=task.body,
                        index_in_course=task.index_in_course,
                    ),
                    where=(tasks_table.c.id == task.id)
                )
            )

        stmt = stmt.returning(tasks_table.c.id)

        res = await self._session.execute(stmt)
        return res.scalar_one()

    async def save_code_task(self, task: CodeTask) -> TaskID:
        upsert_code_task_stmt = (
            insert(tasks_table).
            values(
                type=task.type,
                title=task.title,
                topic=task.topic,
                body=task.body,
                course_id=task.course_id,
                index_in_course=task.index_in_course,
                prepared_code=task.prepared_code,
                code_duration_timeout=task.code_duration_timeout,
            ).
            returning(tasks_table.c.id)
        )

        if task.id:
            for idx, test in enumerate(task.tests):
                if test.code is None:
                    await self._session.delete(test)
                    return task.id

            upsert_code_task_stmt = (
                insert(tasks_table).
                values(
                    id=task.id,
                    type=task.type,
                    title=task.title,
                    topic=task.topic,
                    body=task.body,
                    course_id=task.course_id,
                    index_in_course=task.index_in_course,
                    prepared_code=task.prepared_code,
                    code_duration_timeout=task.code_duration_timeout,
                ).
                on_conflict_do_update(
                    constraint='tasks_pkey',
                    set_=dict(
                        title=task.title,
                        topic=task.topic,
                        body=task.body,
                        index_in_course=task.index_in_course,
                        prepared_code=task.prepared_code,
                        code_duration_timeout=task.code_duration_timeout,
                    ),
                    where=(tasks_table.c.id == task.id)
                ).
                returning(tasks_table.c.id)
            )

        res = await self._session.execute(upsert_code_task_stmt)
        task_id = res.scalar_one()

        task.tests = list(filter(lambda t: t.code is not None, task.tests))

        insert_code_task_tests_stmt = (
            insert(CodeTaskTest).
            values(
                [
                    {"index_in_task": idx, "code": test.code, "task_id": task_id}
                    for idx, test in enumerate(task.tests)
                ]
            )
        )
        insert_code_task_tests_stmt = insert_code_task_tests_stmt.on_conflict_do_update(
            constraint='code_task_tests_pkey',
            set_=dict(code=insert_code_task_tests_stmt.excluded.code),
        )

        await self._session.execute(insert_code_task_tests_stmt)
        return task_id

    async def save_poll_task(self, task: PollTask) -> TaskID:
        task_upsert_stmt = (
            insert(tasks_table).
            values(
                type=task.type,
                title=task.title,
                topic=task.topic,
                body=task.body,
                course_id=task.course_id,
                index_in_course=task.index_in_course
            )
        )

        if task.id:
            task_upsert_stmt = (
                insert(tasks_table).
                values(
                    id=task.id,
                    type=task.type,
                    title=task.title,
                    topic=task.topic,
                    body=task.body,
                    course_id=task.course_id,
                    index_in_course=task.index_in_course
                )
            ).on_conflict_do_update(
                constraint='tasks_pkey',
                set_=dict(
                    title=task.title,
                    topic=task.topic,
                    body=task.body,
                    index_in_course=task.index_in_course,
                ),
                where=(tasks_table.c.id == task.id)
            )

        task_upsert_stmt = task_upsert_stmt.returning(tasks_table.c.id)
        insert_options_stmt = (
            insert(poll_task_options_table).
            values([
                {'id': option.id, 'content': option.content, 'is_correct': option.is_correct}
                for option in task.options
            ])
        )
        insert_options_stmt = insert_options_stmt.on_conflict_do_update(
            constraint='poll_task_options_pkey',
            set_=dict(code=insert_options_stmt.excluded.code),
        )

        res, _ = await self._session.execute(task_upsert_stmt)
        await self._session.execute(insert_options_stmt)

        return res.scalar_one()

    async def delete(self, task_id: TaskID) -> None:
        stmt = (
            delete(tasks_table).
            where(
                tasks_table.c.id == task_id,
            )
        )
        await self._session.execute(stmt)
