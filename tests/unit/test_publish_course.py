from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from learn_anything.course_platform.application.interactors.course.publish_course import (
    PublishCourseInteractor,
    PublishCourseInputData,
)
from learn_anything.course_platform.domain.entities.course.errors import (
    CourseAlreadyPublishedError,
    CourseDoesNotExistError,
    NeedAtLeastOneTaskToPublishCourseError,
)
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID
from learn_anything.course_platform.domain.entities.user.models import UserID


ACTOR_ID = 100
COURSE_ID = CourseID(1)
NOW = datetime.now()


@pytest.mark.asyncio
async def test_publish_course_success(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
    task_gateway_mock: AsyncMock,
    commiter_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID

    course = Course(
        id=COURSE_ID,
        title="My Course",
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
    task_gateway_mock.total_with_course.return_value = 3

    interactor = ioc_container.get(PublishCourseInteractor)
    result = await interactor.execute(PublishCourseInputData(course_id=COURSE_ID))

    assert result == "My Course"
    assert course.is_published is True
    course_gateway_mock.save.assert_awaited_once()
    commiter_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_course_not_found_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course_gateway_mock.with_id.return_value = None

    interactor = ioc_container.get(PublishCourseInteractor)

    with pytest.raises(CourseDoesNotExistError):
        await interactor.execute(PublishCourseInputData(course_id=COURSE_ID))


@pytest.mark.asyncio
async def test_publish_course_already_published_raises(
    ioc_container,
    id_provider_mock: AsyncMock,
    course_gateway_mock: AsyncMock,
):
    id_provider_mock.get_current_user_id.return_value = ACTOR_ID
    course = Course(
        id=COURSE_ID,
        title="C",
        description="D",
        photo_id=None,
        creator_id=UserID(ACTOR_ID),
        is_published=True,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []

    interactor = ioc_container.get(PublishCourseInteractor)

    with pytest.raises(CourseAlreadyPublishedError):
        await interactor.execute(PublishCourseInputData(course_id=COURSE_ID))


@pytest.mark.asyncio
async def test_publish_course_no_tasks_raises(
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
        creator_id=UserID(ACTOR_ID),
        is_published=False,
        registrations_limit=None,
        total_registered=0,
        created_at=NOW,
        updated_at=NOW,
    )
    course_gateway_mock.with_id.return_value = course
    course_gateway_mock.get_share_rules.return_value = []
    task_gateway_mock.total_with_course.return_value = 0

    interactor = ioc_container.get(PublishCourseInteractor)

    with pytest.raises(NeedAtLeastOneTaskToPublishCourseError):
        await interactor.execute(PublishCourseInputData(course_id=COURSE_ID))
