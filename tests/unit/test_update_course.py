from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.interactors.course.update_course import (
    UpdateCourseInteractor,
    UpdateCourseInputData,
    UpdateCourseOutputData,
)
from learn_anything.course_platform.domain.entities.course.errors import CourseDoesNotExistError
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
COURSE_ID = CourseID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_update_course_title_and_description(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    file_manager_mock: AsyncMock,
    commiter_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="Old",
        description="OldDesc",
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
    course_gateway_mock.save.return_value = COURSE_ID

    interactor = ioc_container.get(UpdateCourseInteractor)
    result = await interactor.execute(
        UpdateCourseInputData(
            course_id=COURSE_ID,
            title="New Title",
            description="New Desc",
            photo_id=None,
            photo=None,
            registrations_limit=None,
        )
    )

    assert isinstance(result, UpdateCourseOutputData)
    assert result.id == COURSE_ID
    assert course.title == "New Title"
    assert course.description == "New Desc"
    course_gateway_mock.save.assert_awaited_once()
    commiter_mock.commit.assert_awaited_once()
    file_manager_mock.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_course_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(UpdateCourseInteractor)

    with pytest.raises(CourseDoesNotExistError):
        await interactor.execute(
            UpdateCourseInputData(course_id=COURSE_ID, photo_id=None, photo=None)
        )
