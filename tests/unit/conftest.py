from unittest.mock import AsyncMock

import pytest
from dishka import Provider, Scope, make_container, Container
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

import learn_anything.course_platform.adapters.persistence.tables  # noqa
from learn_anything.course_platform.application.interactors.course.create_course import CreateCourseInteractor
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.committer import Commiter
from learn_anything.course_platform.application.ports.data.course_gateway import CourseGateway
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway


@pytest.fixture(scope='function')
def course_gateway_mock():
    return AsyncMock()


@pytest.fixture(scope='function')
def user_gateway_mock():
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


@pytest.fixture(scope="function")
def ioc_container(
        course_gateway_mock: AsyncMock,
        user_gateway_mock: AsyncMock,
        sa_session_mock: AsyncMock,
        commiter_mock: AsyncMock,
        file_manager_mock: AsyncMock,
        id_provider_mock: AsyncMock,
) -> Container:
    provider = Provider()

    provider.provide(lambda: course_gateway_mock, scope=Scope.APP, provides=CourseGateway)
    provider.provide(lambda: user_gateway_mock, scope=Scope.APP, provides=UserGateway)
    provider.provide(lambda: sa_session_mock, scope=Scope.APP, provides=AsyncSession)
    provider.provide(lambda: commiter_mock, scope=Scope.APP, provides=Commiter)
    provider.provide(lambda: file_manager_mock, scope=Scope.APP, provides=FileManager)
    provider.provide(lambda: id_provider_mock, scope=Scope.APP, provides=IdentityProvider)

    provider.provide(CreateCourseInteractor, scope=Scope.APP)

    container = make_container(provider)
    return container
