from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.input_data import Pagination
from learn_anything.course_platform.application.interactors.task.get_course_tasks import (
    GetCourseTasksInteractor,
    GetCourseTasksInputData,
)
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.task.enums import TaskType
from learn_anything.course_platform.domain.entities.task.models import Task, TaskID
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
COURSE_ID = CourseID(1)
TASK_ID = TaskID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_get_course_tasks_theory_only(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    task_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="C",
        description="D",
        photo_id=None,
        creator_id=UserID(1),
        is_published=True,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []

    task = Task(
        id=TASK_ID,
        type=TaskType.THEORY,
        topic="Basics",
        title="T1",
        body="B1",
        course_id=COURSE_ID,
        index_in_course=0,
        created_at=NOW,
        updated_at=NOW,
    )
    task_gateway_mock.with_course.return_value = ([task], 1)

    interactor = ioc_container.get(GetCourseTasksInteractor)
    result = await interactor.execute(
        GetCourseTasksInputData(
            course_id=COURSE_ID,
            pagination=Pagination(offset=0, limit=10),
            filters=None,
        )
    )

    assert result.total == 1
    assert len(result.tasks) == 1
    assert result.tasks[0].title == "T1"
    assert result.tasks[0].body == "B1"
    assert result.tasks[0].type == TaskType.THEORY

    task_gateway_mock.with_course.assert_awaited_once()
