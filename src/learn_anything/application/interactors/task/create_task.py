import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.playground import PlaygroundFactory, CodeIsInvalidError
from learn_anything.entities.course.errors import CourseDoesNotExistError
from learn_anything.entities.course.models import CourseID
from learn_anything.entities.course.rules import ensure_actor_has_write_access
from learn_anything.entities.task.errors import TaskTestCodeIsInvalidError, TaskPreparedCodeIsInvalidError
from learn_anything.entities.task.models import TaskType, TaskID, PollTask, PollTaskOption, Task
from learn_anything.entities.task.rules import create_code_task
from learn_anything.entities.user.models import UserID


@dataclass
class CreateTaskInputData:
    course_id: CourseID
    title: str
    body: str
    topic: str | None
    task_type: TaskType
    index_in_course: int


@dataclass
class CreateTaskOutputData:
    task_id: TaskID
    created_at: datetime


class CreateTaskInteractor:
    def __init__(self, id_provider: IdentityProvider, task_gateway: TaskGateway, course_gateway: CourseGateway,
                 commiter: Commiter) -> None:
        self._id_provider = id_provider
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._commiter = commiter

    async def execute(self, data: CreateTaskInputData) -> CreateTaskOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        share_rules = await self._course_gateway.get_share_rules(course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        task = Task(
            id=None,
            title=data.title,
            topic=data.topic,
            type=data.task_type,
            body=data.body,
            course_id=data.course_id,
            index_in_course=data.index_in_course,
            created_at=datetime.now()
        )
        new_task_id = await self._task_gateway.save(task=task)

        await self._commiter.commit()

        return CreateTaskOutputData(task_id=new_task_id, created_at=task.created_at)


@dataclass
class CreateCodeTaskInputData:
    course_id: CourseID
    task_type: TaskType
    title: str
    body: str
    topic: str | None
    index_in_course: int
    prepared_code: str | None
    code_duration_timeout: int
    attempts_limit: int | None
    tests: Sequence[str]


@dataclass
class CreateCodeTaskOutputData:
    task_id: TaskID


class CreateCodeTaskInteractor:
    def __init__(
            self,
            id_provider: IdentityProvider,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            playground_factory: PlaygroundFactory,
            commiter: Commiter
    ) -> None:
        self._id_provider = id_provider
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._playground_factory = playground_factory
        self._commiter = commiter

    async def execute(self, data: CreateCodeTaskInputData) -> CreateCodeTaskOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        share_rules = await self._course_gateway.get_share_rules(course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        await self._ensure_codes_are_valid(
            actor_id=actor_id,
            task_prepared_code=data.prepared_code,
            code_duration_timeout=data.code_duration_timeout,
            codes_of_tests=data.tests,
        )

        task = create_code_task(
            title=data.title,
            body=data.body,
            topic=data.topic,
            course_id=data.course_id,
            index_in_course=data.index_in_course,
            prepared_code=data.prepared_code,
            code_duration_timeout=data.code_duration_timeout,
            tests=data.tests,
            attempts_limit=data.attempts_limit,
        )
        new_task_id = await self._task_gateway.save_code_task(task=task)

        await self._commiter.commit()

        return CreateCodeTaskOutputData(task_id=new_task_id)

    async def _ensure_codes_are_valid(
            self,
            actor_id: UserID,
            task_prepared_code: str | None,
            codes_of_tests: Sequence[str],
            code_duration_timeout: int,
    ):
        async with self._playground_factory.create(
                identifier=None,
                code_duration_timeout=code_duration_timeout,
        ) as pl:
            if task_prepared_code:
                _, err = await pl.execute_code(code=task_prepared_code)
                if err:
                    raise TaskPreparedCodeIsInvalidError(code=task_prepared_code, err=err)

            check_tests_tasks = []
            code_index_mapping = {}
            for index, code in enumerate(codes_of_tests):
                # prevent expected errors
                code = (
                    f'from contextlib import suppress\n'
                    '\n'
                    'stdout, stderr = "stub", "stub"\n'
                    f'with suppress(AssertionError, NameError):\n'
                    f'    {code}'
                )

                task = asyncio.create_task(pl.execute_code(
                    code=code,
                    raise_exc_on_err=True
                ))
                check_tests_tasks.append(task)

                code_index_mapping[code] = index

            done, pending = await asyncio.wait(check_tests_tasks, return_when=asyncio.FIRST_EXCEPTION)
            if not pending:
                return

            for task in pending:
                task.cancel()

            for task in done:
                exc: BaseException | None = task.exception()
                if exc is None:
                    continue

                if isinstance(exc, CodeIsInvalidError):
                    raise TaskTestCodeIsInvalidError(
                        user_id=actor_id,
                        index=code_index_mapping[code],
                        code=exc.code,
                        err=exc.err
                    )

                raise exc


@dataclass
class Option:
    content: str
    is_correct: bool


@dataclass
class CreatePollTaskInputData:
    course_id: CourseID
    task_type: TaskType
    title: str
    topic: str | None
    body: str
    index_in_course: int
    attempts_limit: int | None
    options: Sequence[Option]


@dataclass
class CreatePollTaskOutputData:
    task_id: TaskID


class CreatePollTaskInteractor:
    def __init__(self, id_provider: IdentityProvider, task_gateway: TaskGateway, course_gateway: CourseGateway,
                 commiter: Commiter) -> None:
        self._id_provider = id_provider
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._commiter = commiter

    async def execute(self, data: CreatePollTaskInputData) -> CreatePollTaskOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        share_rules = await self._course_gateway.get_share_rules(course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        task = PollTask(
            id=None,
            title=data.title,
            type=data.task_type,
            body=data.body,
            topic=data.topic,
            course_id=data.course_id,
            index_in_course=data.index_in_course,
            attempts_limit=data.attempts_limit,
            options=[
                PollTaskOption(
                    id=None,
                    content=option.content,
                    is_correct=option.is_correct,
                )
                for option in data.options
            ],
            created_at=datetime.now()
        )
        new_task_id = await self._task_gateway.save_poll_task(task=task)

        await self._commiter.commit()

        return CreatePollTaskOutputData(task_id=new_task_id)
