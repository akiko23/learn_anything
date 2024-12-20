import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.committer import Commiter
from learn_anything.course_platform.application.ports.data.course_gateway import CourseGateway
from learn_anything.course_platform.application.ports.data.task_gateway import TaskGateway
from learn_anything.course_platform.application.ports.playground import PlaygroundFactory, CodeIsInvalidError
from learn_anything.course_platform.domain.entities.course.errors import CourseDoesNotExistError
from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.domain.entities.course.rules import ensure_actor_has_write_access
from learn_anything.course_platform.domain.entities.task.enums import TaskType
from learn_anything.course_platform.domain.entities.task.errors import TaskTestCodeIsInvalidError, \
    TaskPreparedCodeIsInvalidError
from learn_anything.course_platform.domain.entities.task.models import TaskID, PollTaskOption
from learn_anything.course_platform.domain.entities.task.rules import create_code_task, create_theory_task, \
    create_poll_task
from learn_anything.course_platform.domain.entities.user.models import UserID

UNSPECIFIED_TASK_ID = TaskID(0)


@dataclass(kw_only=True)
class CreateTheoryTaskInputData:
    id: TaskID = UNSPECIFIED_TASK_ID
    course_id: CourseID
    title: str
    body: str
    topic: str | None
    task_type: TaskType
    index_in_course: int


@dataclass
class CreateTheoryTaskOutputData:
    task_id: TaskID
    created_at: datetime
    updated_at: datetime


class CreateTaskInteractor:
    def __init__(self, id_provider: IdentityProvider, task_gateway: TaskGateway, course_gateway: CourseGateway,
                 commiter: Commiter) -> None:
        self._id_provider = id_provider
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._commiter = commiter

    async def execute(self, data: CreateTheoryTaskInputData) -> CreateTheoryTaskOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        course = await self._course_gateway.with_id(data.course_id)
        if not course:
            raise CourseDoesNotExistError(data.course_id)

        share_rules = await self._course_gateway.get_share_rules(course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        task = create_theory_task(
            id_=data.id,
            title=data.title,
            topic=data.topic,
            body=data.body,
            course_id=data.course_id,
            index_in_course=data.index_in_course,
        )
        new_task_id = await self._task_gateway.save(task=task)

        await self._commiter.commit()

        return CreateTheoryTaskOutputData(task_id=new_task_id, created_at=task.created_at, updated_at=course.updated_at)


@dataclass(kw_only=True)
class CreateCodeTaskInputData:
    id: TaskID = UNSPECIFIED_TASK_ID
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
            id_=data.id,
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
    ) -> None:
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

                task: asyncio.Task[tuple[str, str]] = asyncio.create_task(pl.execute_code(
                    code=code,
                    raise_exc_on_err=True
                ))
                check_tests_tasks.append(task)

                code_index_mapping[code] = index

            done, pending = await asyncio.wait(check_tests_tasks, return_when=asyncio.FIRST_EXCEPTION)

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


@dataclass(kw_only=True)
class CreatePollTaskInputData:
    id: TaskID = UNSPECIFIED_TASK_ID
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

        task = create_poll_task(
            id_=data.id,
            title=data.title,
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
        )
        new_task_id = await self._task_gateway.save_poll_task(task=task)

        await self._commiter.commit()

        return CreatePollTaskOutputData(task_id=new_task_id)
