from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.interactors.course.register_for_course import (
    RegisterForCourseInteractor,
    RegisterForCourseInputData,
)
from learn_anything.course_platform.domain.entities.course.errors import (
    CourseDoesNotExistError,
    UserAlreadyRegisteredForCourseError,
)
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
COURSE_ID = CourseID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_register_for_course_success(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    registration_for_course_gateway_mock: AsyncMock,
    commiter_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="Published Course",
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

    interactor = ioc_container.get(RegisterForCourseInteractor)
    await interactor.execute(RegisterForCourseInputData(course_id=COURSE_ID))

    course_gateway_mock.save.assert_awaited_once()
    registration_for_course_gateway_mock.save.assert_awaited_once()
    commiter_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_for_course_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(RegisterForCourseInteractor)

    with pytest.raises(CourseDoesNotExistError):
        await interactor.execute(RegisterForCourseInputData(course_id=COURSE_ID))


@pytest.mark.asyncio
async def test_register_for_course_not_published_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course = Course(
        id=COURSE_ID,
        title="Draft",
        description="D",
        photo_id=None,
        creator_id=UserID(1),
        is_published=False,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course

    interactor = ioc_container.get(RegisterForCourseInteractor)

    with pytest.raises(CourseDoesNotExistError):
        await interactor.execute(RegisterForCourseInputData(course_id=COURSE_ID))


@pytest.mark.asyncio
async def test_register_for_course_already_registered_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    registration_for_course_gateway_mock: AsyncMock,
):
    from learn_anything.course_platform.domain.entities.course.models import (
        RegistrationForCourse,
    )

    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course = Course(
        id=COURSE_ID,
        title="Course",
        description="D",
        photo_id=None,
        creator_id=UserID(1),
        is_published=True,
        registrations_limit=None,
        total_registered=1,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    registration_for_course_gateway_mock.read.return_value = RegistrationForCourse(
        user_id=UserID(ACTOR_ID), course_id=COURSE_ID, created_at=NOW
    )

    interactor = ioc_container.get(RegisterForCourseInteractor)

    with pytest.raises(UserAlreadyRegisteredForCourseError) as exc_info:
        await interactor.execute(RegisterForCourseInputData(course_id=COURSE_ID))

    assert exc_info.value.course_title == "Course"
