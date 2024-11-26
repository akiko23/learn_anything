
from aiogram.types import TelegramObject

from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)

from learn_anything.application.interactors.auth.create_auth_link import CreateAuthLinkInteractor
from learn_anything.application.interactors.auth.invalidate_auth_link import InvalidateAuthLinkInteractor
from learn_anything.application.interactors.course.create_course import CreateCourseInteractor
from learn_anything.application.interactors.course.delete_course import DeleteCourseInteractor
from learn_anything.application.interactors.course.get_course import GetCourseInteractor
from learn_anything.application.interactors.course.get_many_courses import GetManyCoursesInteractor
from learn_anything.application.interactors.course.leave_course import LeaveCourseInteractor
from learn_anything.application.interactors.course.publish_course import PublishCourseInteractor
from learn_anything.application.interactors.course.register_for_course import RegisterForCourseInteractor
from learn_anything.application.interactors.course.update_course import UpdateCourseInteractor
from learn_anything.application.interactors.task.delete_task import DeleteTaskInteractor
from learn_anything.application.interactors.task.update_task import UpdateTaskInteractor, UpdateCodeTaskInteractor
from learn_anything.application.interactors.submission.create_submission import CreateCodeTaskSubmissionInteractor, \
    CreatePollTaskSubmissionInteractor
from learn_anything.application.interactors.task.create_task import CreateCodeTaskInteractor, CreatePollTaskInteractor, \
    CreateTaskInteractor
from learn_anything.application.interactors.task.get_course_tasks import GetCourseTasksInteractor
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.auth.token import TokenProcessor
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.application.interactors.auth.authenticate import Authenticate
from learn_anything.application.ports.playground import PlaygroundFactory
from learn_anything.adapters.auth.tg_auth import TgIdentityProvider, TgB64TokenProcessor
from learn_anything.adapters.persistence.commiter import SACommiter
from learn_anything.adapters.persistence.config import load_db_config, DatabaseConfig
from learn_anything.adapters.persistence.mappers.course import CourseMapper, RegistrationForCourseMapper
from learn_anything.adapters.persistence.mappers.submission import SubmissionMapper
from learn_anything.adapters.persistence.mappers.task import TaskMapper
from learn_anything.adapters.persistence.mappers.user import UserMapper, AuthLinkMapper
from learn_anything.adapters.persistence.providers import get_async_sessionmaker, get_engine, get_async_session
from learn_anything.adapters.playground.unix_playground import UnixPlaygroundFactory
from learn_anything.adapters.s3.config import load_s3_config, S3Config
from learn_anything.adapters.s3.s3_file_manager import S3FileManager
from learn_anything.presentation.tg_bot.config import load_bot_config, BotConfig


def gateways_provider() -> Provider:
    provider = Provider()

    provider.provide(UserMapper, scope=Scope.REQUEST, provides=UserGateway)
    provider.provide(AuthLinkMapper, scope=Scope.REQUEST, provides=AuthLinkGateway)

    provider.provide(CourseMapper, scope=Scope.REQUEST, provides=CourseGateway)
    provider.provide(RegistrationForCourseMapper, scope=Scope.REQUEST,provides=RegistrationForCourseGateway)

    provider.provide(TaskMapper, scope=Scope.REQUEST, provides=TaskGateway)

    provider.provide(SubmissionMapper, scope=Scope.REQUEST, provides=SubmissionGateway)

    provider.provide(SACommiter, scope=Scope.REQUEST, provides=Commiter)

    return provider


def infrastructure_provider() -> Provider:
    provider = Provider()

    provider.provide(TgB64TokenProcessor, scope=Scope.REQUEST, provides=TokenProcessor)
    provider.provide(S3FileManager, scope=Scope.REQUEST, provides=FileManager)
    provider.provide(UnixPlaygroundFactory, scope=Scope.REQUEST, provides=PlaygroundFactory)

    return provider


def interactors_provider() -> Provider:
    provider = Provider()

    provider.provide(Authenticate, scope=Scope.REQUEST)
    provider.provide(CreateAuthLinkInteractor, scope=Scope.REQUEST)
    provider.provide(InvalidateAuthLinkInteractor, scope=Scope.REQUEST)

    provider.provide(CreateCourseInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateCourseInteractor, scope=Scope.REQUEST)
    provider.provide(GetCourseInteractor, scope=Scope.REQUEST)
    provider.provide(GetCourseTasksInteractor, scope=Scope.REQUEST)
    provider.provide(GetManyCoursesInteractor, scope=Scope.REQUEST)
    provider.provide(RegisterForCourseInteractor, scope=Scope.REQUEST)
    provider.provide(LeaveCourseInteractor, scope=Scope.REQUEST)
    provider.provide(PublishCourseInteractor, scope=Scope.REQUEST)
    provider.provide(DeleteCourseInteractor, scope=Scope.REQUEST)

    provider.provide(CreateTaskInteractor, scope=Scope.REQUEST)
    provider.provide(CreateCodeTaskInteractor, scope=Scope.REQUEST)
    provider.provide(CreatePollTaskInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateTaskInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateCodeTaskInteractor, scope=Scope.REQUEST)
    provider.provide(DeleteTaskInteractor, scope=Scope.REQUEST)

    provider.provide(CreateCodeTaskSubmissionInteractor, scope=Scope.REQUEST)
    provider.provide(CreatePollTaskSubmissionInteractor, scope=Scope.REQUEST)

    return provider


def configs_provider() -> Provider:
    provider = Provider()

    provider.provide(lambda: load_db_config(), scope=Scope.APP, provides=DatabaseConfig)
    provider.provide(lambda: load_bot_config(), scope=Scope.APP, provides=BotConfig)
    provider.provide(lambda: load_s3_config(), scope=Scope.APP, provides=S3Config)

    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, obj: TelegramObject) -> int:
        return obj.from_user.id


    @provide(scope=Scope.REQUEST)
    async def get_identity_provider(
            self,
            user_id: int,
            user_gateway: UserGateway,
            auth_link_gateway: AuthLinkGateway,
            token_processor: TokenProcessor,
    ) -> IdentityProvider:
        identity_provider = TgIdentityProvider(
            user_id=user_id,
            user_gateway=user_gateway,
            auth_link_gateway=auth_link_gateway,
            token_processor=token_processor,
        )

        return identity_provider


def db_provider() -> Provider:
    provider = Provider()

    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(get_async_session, scope=Scope.REQUEST)

    return provider


def setup_providers() -> list[Provider]:
    providers = [
        gateways_provider(),
        infrastructure_provider(),
        db_provider(),
        configs_provider(),
        interactors_provider(),
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
