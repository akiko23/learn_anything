from typing import BinaryIO
from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import Container

from learn_anything.course_platform.application.interactors.course.create_course import CreateCourseInteractor, \
    CreateCourseInputData
from learn_anything.course_platform.application.ports.data.file_manager import COURSES_DEFAULT_DIRECTORY

TEST_COURSE_CREATOR_ID = 12345

TEST_COURSE_PHOTO_ID = 'fKSKFk131341FAKFSL'
TEST_COURSE_PHOTO_PATH = f'{COURSES_DEFAULT_DIRECTORY}/{TEST_COURSE_PHOTO_ID}'

TEST_NEW_COURSE_ID = 123


@pytest.mark.asyncio
async def test_create_course(
        ioc_container: Container,
        id_provider_mock: AsyncMock,
        file_manager_mock: AsyncMock,
        course_gateway_mock: AsyncMock,
):
    course_input_data = CreateCourseInputData(
        title='test1',
        description='testdesc',
        photo_id=TEST_COURSE_PHOTO_ID,
        photo=BinaryIO(),
        registrations_limit=None,
    )

    id_provider_mock.get_current_user_id.return_value = TEST_COURSE_CREATOR_ID

    file_manager_mock.generate_path = MagicMock()
    file_manager_mock.generate_path.return_value = TEST_COURSE_PHOTO_PATH

    file_manager_mock.save.return_value = None
    course_gateway_mock.save.return_value = TEST_NEW_COURSE_ID

    interactor = ioc_container.get(CreateCourseInteractor)

    output_data = await interactor.execute(data=course_input_data)

    assert output_data.id == TEST_NEW_COURSE_ID

    id_provider_mock.get_current_user_id.assert_called_once()
    file_manager_mock.generate_path.assert_called_once_with(
        directories=(COURSES_DEFAULT_DIRECTORY,),
        filename=TEST_COURSE_PHOTO_ID,
    )
    file_manager_mock.save.assert_awaited_once()
    course_gateway_mock.save.assert_awaited_once()
