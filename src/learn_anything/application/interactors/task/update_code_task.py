from dataclasses import dataclass
from datetime import datetime

from typing import Literal

from learn_anything.application.input_data import UNSET
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.course_gateway import CourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.application.ports.playground import PlaygroundFactory
from learn_anything.domain.course.errors import CourseDoesNotExistError
from learn_anything.domain.course.rules import ensure_actor_has_write_access
from learn_anything.domain.task.models import TaskID, CodeTaskTestID
from learn_anything.domain.task.rules import update_code_task_test


@dataclass
class UpdateCodeTaskInputData:
    task_id: TaskID
    prepared_code: str | Literal['UNSET'] = None
    code_duration_timeout: int | None = None
    attempts_limit: int | Literal['UNSET'] = None


@dataclass
class UpdateCodeTaskOutputData:
    id: TaskID | None = None
    err: str | None = None


class UpdateCodeTaskInteractor:
    def __init__(
            self,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            user_gateway: UserGateway,
            id_provider: IdentityProvider,
            playground_factory: PlaygroundFactory,
            file_manager: FileManager, commiter: Commiter
    ) -> None:
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._user_gateway = user_gateway
        self._commiter = commiter
        self._id_provider = id_provider
        self._playground_factory = playground_factory
        self._file_manager = file_manager

    async def execute(self, data: UpdateCodeTaskInputData) -> UpdateCodeTaskOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        task = await self._task_gateway.get_code_task_with_id(data.task_id)
        if not task:
            raise CourseDoesNotExistError

        course = await self._course_gateway.with_id(task.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        if data.prepared_code:
            if data.prepared_code != UNSET:
                async with self._playground_factory.create(
                        code_duration_timeout=task.code_duration_timeout,
                ) as pl:
                    out, err = await pl.execute_code(code=data.prepared_code)
                    if err:
                        return UpdateCodeTaskOutputData(err=err)

                task.prepared_code = data.prepared_code
            else:
                task.prepared_code = None

        if data.attempts_limit:
            task.attempts_limit = None if data.attempts_limit == UNSET else data.attempts_limit

        if data.code_duration_timeout:
            task.code_duration_timeout = data.code_duration_timeout

        task.updated_at = datetime.now()
        course.updated_at = datetime.now()

        updated_task_id = await self._task_gateway.save_code_task(task=task)
        await self._course_gateway.save(course=course)

        await self._commiter.commit()

        return UpdateCodeTaskOutputData(id=updated_task_id)


@dataclass
class UpdateCodeTaskTestInputData:
    id: CodeTaskTestID
    task_id: TaskID
    code: str | None = None


@dataclass
class UpdateCodeTaskTestOutputData:
    new_code: str


class UpdateCodeTaskTestInteractor:
    def __init__(
            self,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            user_gateway: UserGateway,
            id_provider: IdentityProvider,
            playground_factory: PlaygroundFactory,
            file_manager: FileManager, commiter: Commiter
    ) -> None:
        self._task_gateway = task_gateway
        self._course_gateway = course_gateway
        self._user_gateway = user_gateway
        self._commiter = commiter
        self._id_provider = id_provider
        self._playground_factory = playground_factory
        self._file_manager = file_manager

    async def execute(self, data: UpdateCodeTaskTestInputData) -> UpdateCodeTaskTestOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        task = await self._task_gateway.get_code_task_with_id(data.task_id)
        if not task:
            raise CourseDoesNotExistError

        course = await self._course_gateway.with_id(task.course_id)

        share_rules = await self._course_gateway.get_share_rules(course_id=course.id)
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)

        if data.code:
            task = update_code_task_test(task=task, new_code=data.code, target_test_id=data.id)

        task.updated_at = datetime.now()
        course.updated_at = datetime.now()

        await self._task_gateway.save_code_task(task=task)
        await self._course_gateway.save(course=course)

        await self._commiter.commit()

        return UpdateCodeTaskTestOutputData(new_code=data.code)