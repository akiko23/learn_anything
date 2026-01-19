from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.interactors.course.delete_course import (
    DeleteCourseInteractor,
    DeleteCourseInputData,
)
from learn_anything.course_platform.domain.entities.course.errors import (
    CourseDoesNotExistError,
    CoursePermissionError,
)
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
CREATOR_ID = 100  # actor is creator
COURSE_ID = CourseID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_delete_course_success(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    file_manager_mock: AsyncMock,
    commiter_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="To Delete",
        description="Desc",
        photo_id="pic1",
        creator_id=UserID(CREATOR_ID),
        is_published=False,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []

    interactor = ioc_container.get(DeleteCourseInteractor)
    await interactor.execute(DeleteCourseInputData(course_id=COURSE_ID))

    course_gateway_mock.delete.assert_awaited_once_with(course_id=COURSE_ID)
    file_manager_mock.delete.assert_awaited_once()
    commiter_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_course_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(DeleteCourseInteractor)

    with pytest.raises(CourseDoesNotExistError):
        await interactor.execute(DeleteCourseInputData(course_id=COURSE_ID))

    course_gateway_mock.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_course_no_write_access_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = 999  # not creator
    course = Course(
        id=COURSE_ID,
        title="Other",
        description="D",
        photo_id=None,
        creator_id=UserID(1),  # different from 999
        is_published=False,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []  # no share rule for 999

    interactor = ioc_container.get(DeleteCourseInteractor)

    with pytest.raises(CoursePermissionError):
        await interactor.execute(DeleteCourseInputData(course_id=COURSE_ID))

    course_gateway_mock.delete.assert_not_awaited()
