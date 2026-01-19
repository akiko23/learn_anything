from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from learn_anything.course_platform.application.interactors.course.get_course import (
    GetCourseInteractor,
    GetCourseInputData,
)
from learn_anything.course_platform.domain.entities.course.errors import CourseDoesNotExistError
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.domain.entities.user.models import User, UserID


ACTOR_ID = 100
CREATOR_ID = 200
COURSE_ID = CourseID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_get_course_success(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    task_gateway_mock: AsyncMock,
    registration_for_course_gateway_mock: AsyncMock,
    user_gateway_mock: AsyncMock,
    file_manager_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="Test Course",
        description="Desc",
        photo_id="photo123",
        creator_id=UserID(CREATOR_ID),
        is_published=True,
        registrations_limit=None,
        total_registered=10,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []

    task_gateway_mock.total_with_course.return_value = 3
    registration_for_course_gateway_mock.read.return_value = None

    creator = User(id=UserID(CREATOR_ID), role=UserRole.STUDENT, fullname="Author Name", username="author")
    user_gateway_mock.with_id.return_value = creator

    file_manager_mock.generate_path = MagicMock(return_value="courses/photo123")

    interactor = ioc_container.get(GetCourseInteractor)
    result = await interactor.execute(GetCourseInputData(course_id=COURSE_ID))

    assert result.id == COURSE_ID
    assert result.title == "Test Course"
    assert result.description == "Desc"
    assert result.is_published is True
    assert result.creator == "Author Name"
    assert result.total_tasks == 3
    assert result.user_is_registered is False
    assert result.photo_id == "photo123"
    assert result.photo_path == "courses/photo123"

    course_gateway_mock.with_id.assert_awaited_once_with(COURSE_ID)
    task_gateway_mock.total_with_course.assert_awaited_once_with(course_id=COURSE_ID)


@pytest.mark.asyncio
async def test_get_course_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(GetCourseInteractor)

    with pytest.raises(CourseDoesNotExistError) as exc_info:
        await interactor.execute(GetCourseInputData(course_id=COURSE_ID))

    assert exc_info.value.course_id == COURSE_ID
