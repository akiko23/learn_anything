from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.interactors.task.delete_task import (
    DeleteTaskInteractor,
    DeleteTaskInputData,
)
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.task.errors import TaskDoesNotExistError
from learn_anything.course_platform.domain.entities.task.enums import TaskType
from learn_anything.course_platform.domain.entities.task.models import Task, TaskID
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
COURSE_ID = CourseID(1)
TASK_ID = TaskID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_delete_task_success(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    task_gateway_mock: AsyncMock,
    commiter_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    task = Task(
        id=TASK_ID,
        type=TaskType.THEORY,
        topic=None,
        title="T",
        body="B",
        course_id=COURSE_ID,
        index_in_course=0,
        created_at=NOW,
        updated_at=NOW,
    )
    task_gateway_mock.with_id.return_value = task

    course = Course(
        id=COURSE_ID,
        title="C",
        description="D",
        photo_id=None,
        creator_id=UserID(ACTOR_ID),
        is_published=False,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []

    interactor = ioc_container.get(DeleteTaskInteractor)
    await interactor.execute(DeleteTaskInputData(task_id=TASK_ID))

    task_gateway_mock.delete.assert_awaited_once_with(task_id=TASK_ID)
    commiter_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_task_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    task_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    task_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(DeleteTaskInteractor)

    with pytest.raises(TaskDoesNotExistError) as exc_info:
        await interactor.execute(DeleteTaskInputData(task_id=TASK_ID))

    assert exc_info.value.task_id == TASK_ID
    task_gateway_mock.delete.assert_not_awaited()
