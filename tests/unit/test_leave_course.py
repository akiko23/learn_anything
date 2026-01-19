from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.interactors.course.leave_course import (
    LeaveCourseInteractor,
    LeaveCourseInputData,
)
from learn_anything.course_platform.domain.entities.course.errors import (
    CourseDoesNotExistError,
    RegistrationForCourseDoesNotExistError,
)
from learn_anything.course_platform.domain.entities.course.models import (
    Course,
    CourseID,
    RegistrationForCourse,
)
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
COURSE_ID = CourseID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_leave_course_success(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    registration_for_course_gateway_mock: AsyncMock,
    commiter_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="Course",
        description="D",
        photo_id=None,
        creator_id=UserID(1),
        is_published=True,
        registrations_limit=10,
        total_registered=1,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    registration_for_course_gateway_mock.read.return_value = RegistrationForCourse(
        user_id=UserID(ACTOR_ID), course_id=COURSE_ID, created_at=NOW
    )

    interactor = ioc_container.get(LeaveCourseInteractor)
    await interactor.execute(LeaveCourseInputData(course_id=COURSE_ID))

    course_gateway_mock.save.assert_awaited_once()
    registration_for_course_gateway_mock.delete.assert_awaited_once_with(
        user_id=UserID(ACTOR_ID), course_id=COURSE_ID
    )
    commiter_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_leave_course_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(LeaveCourseInteractor)

    with pytest.raises(CourseDoesNotExistError):
        await interactor.execute(LeaveCourseInputData(course_id=COURSE_ID))


@pytest.mark.asyncio
async def test_leave_course_not_registered_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    registration_for_course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course = Course(
        id=COURSE_ID,
        title="Course",
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
    registration_for_course_gateway_mock.read.return_value = None

    interactor = ioc_container.get(LeaveCourseInteractor)

    with pytest.raises(RegistrationForCourseDoesNotExistError):
        await interactor.execute(LeaveCourseInputData(course_id=COURSE_ID))
