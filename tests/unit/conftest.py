from unittest.mock import AsyncMock

import pytest
from dishka import Provider, Scope, make_container, Container
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

import learn_anything.course_platform.adapters.persistence.tables  # noqa
from learn_anything.course_platform.application.interactors.course.create_course import CreateCourseInteractor
from learn_anything.course_platform.application.interactors.course.delete_course import DeleteCourseInteractor
from learn_anything.course_platform.application.interactors.course.get_course import GetCourseInteractor
from learn_anything.course_platform.application.interactors.course.leave_course import LeaveCourseInteractor
from learn_anything.course_platform.application.interactors.course.publish_course import (
    PublishCourseInteractor,
)
from learn_anything.course_platform.application.interactors.course.register_for_course import (
    RegisterForCourseInteractor,
)
from learn_anything.course_platform.application.interactors.course.update_course import (
    UpdateCourseInteractor,
)
from learn_anything.course_platform.application.interactors.task.delete_task import DeleteTaskInteractor
from learn_anything.course_platform.application.interactors.task.get_course_tasks import (
    GetCourseTasksInteractor,
)
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.committer import Commiter
from learn_anything.course_platform.application.ports.data.course_gateway import (
    CourseGateway,
    RegistrationForCourseGateway,
)
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.course_platform.application.ports.data.task_gateway import TaskGateway
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway


@pytest.fixture(scope='function')
def course_gateway_mock():
    return AsyncMock()


@pytest.fixture(scope='function')
def user_gateway_mock():
    return AsyncMock()


@pytest.fixture(scope='function')
def task_gateway_mock():
    return AsyncMock()


@pytest.fixture(scope='function')
def registration_for_course_gateway_mock():
    return AsyncMock()


@pytest.fixture(scope='function')
def sa_session_mock():
    return AsyncMock()


@pytest.fixture(scope='function')
def commiter_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope='function')
def file_manager_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope='function')
def id_provider_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope='function')
def submission_gateway_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope="function")
def ioc_container(
        course_gateway_mock: AsyncMock,
        user_gateway_mock: AsyncMock,
        task_gateway_mock: AsyncMock,
        registration_for_course_gateway_mock: AsyncMock,
        submission_gateway_mock: AsyncMock,
        sa_session_mock: AsyncMock,
        commiter_mock: AsyncMock,
        file_manager_mock: AsyncMock,
        id_provider_mock: AsyncMock,
) -> Container:
    provider = Provider()

    provider.provide(lambda: course_gateway_mock, scope=Scope.APP, provides=CourseGateway)
    provider.provide(lambda: user_gateway_mock, scope=Scope.APP, provides=UserGateway)
    provider.provide(lambda: task_gateway_mock, scope=Scope.APP, provides=TaskGateway)
    provider.provide(
        lambda: registration_for_course_gateway_mock,
        scope=Scope.APP,
        provides=RegistrationForCourseGateway,
    )
    provider.provide(lambda: submission_gateway_mock, scope=Scope.APP, provides=SubmissionGateway)
    provider.provide(lambda: sa_session_mock, scope=Scope.APP, provides=AsyncSession)
    provider.provide(lambda: commiter_mock, scope=Scope.APP, provides=Commiter)
    provider.provide(lambda: file_manager_mock, scope=Scope.APP, provides=FileManager)
    provider.provide(lambda: id_provider_mock, scope=Scope.APP, provides=IdentityProvider)

    provider.provide(CreateCourseInteractor, scope=Scope.APP)
    provider.provide(GetCourseInteractor, scope=Scope.APP)
    provider.provide(DeleteCourseInteractor, scope=Scope.APP)
    provider.provide(RegisterForCourseInteractor, scope=Scope.APP)
    provider.provide(LeaveCourseInteractor, scope=Scope.APP)
    provider.provide(PublishCourseInteractor, scope=Scope.APP)
    provider.provide(UpdateCourseInteractor, scope=Scope.APP)
    provider.provide(GetCourseTasksInteractor, scope=Scope.APP)
    provider.provide(DeleteTaskInteractor, scope=Scope.APP)

    container = make_container(provider)
    return container
