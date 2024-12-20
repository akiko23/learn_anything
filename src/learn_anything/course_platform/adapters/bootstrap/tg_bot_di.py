import json
import os
from functools import partial

from aio_pika import Connection
from aio_pika.abc import AbstractChannel
from aio_pika.pool import Pool
from aiogram import Bot, Dispatcher
from aiogram.enums import MessageEntityType
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import TelegramObject, Message
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)

from learn_anything.course_platform.adapters.auth.tg_auth_manager import TelegramAuthManager
from learn_anything.course_platform.adapters.auth.tg_identity_provider import TgIdentityProvider, TgB64TokenProcessor
from learn_anything.course_platform.adapters.json_serializers import DTOJSONEncoder, dto_obj_hook
from learn_anything.course_platform.adapters.persistence.commiter import SACommiter
from learn_anything.course_platform.adapters.persistence.config import load_db_config, DatabaseConfig
from learn_anything.course_platform.adapters.persistence.mappers.course import CourseMapper, RegistrationForCourseMapper
from learn_anything.course_platform.adapters.persistence.mappers.submission import SubmissionMapper
from learn_anything.course_platform.adapters.persistence.mappers.task import TaskMapper
from learn_anything.course_platform.adapters.persistence.mappers.user import UserMapper, AuthLinkMapper
from learn_anything.course_platform.adapters.persistence.providers import get_async_sessionmaker, get_engine, \
    get_async_session
from learn_anything.course_platform.adapters.playground.unix_playground import UnixPlaygroundFactory
from learn_anything.course_platform.adapters.redis.config import load_redis_config, RedisConfig
from learn_anything.course_platform.adapters.rmq.config import load_rmq_config, RMQConfig
from learn_anything.course_platform.adapters.rmq.providers import get_channel, get_connection_pool
from learn_anything.course_platform.adapters.s3.config import load_s3_config, S3Config
from learn_anything.course_platform.adapters.s3.s3_file_manager import S3FileManager
from learn_anything.course_platform.application.interactors.auth.authenticate import AuthenticateInteractor
from learn_anything.course_platform.application.interactors.auth.register import RegisterInteractor
from learn_anything.course_platform.application.interactors.auth_link.create_auth_link import CreateAuthLinkInteractor
from learn_anything.course_platform.application.interactors.auth_link.invalidate_auth_link import \
    InvalidateAuthLinkInteractor
from learn_anything.course_platform.application.interactors.auth_link.login_with_auth_link import \
    LoginWithAuthLinkInteractor
from learn_anything.course_platform.application.interactors.course.create_course import CreateCourseInteractor
from learn_anything.course_platform.application.interactors.course.delete_course import DeleteCourseInteractor
from learn_anything.course_platform.application.interactors.course.get_course import GetCourseInteractor
from learn_anything.course_platform.application.interactors.course.get_many_courses import GetAllCoursesInteractor, \
    GetActorCreatedCoursesInteractor, GetActorRegisteredCoursesInteractor
from learn_anything.course_platform.application.interactors.course.leave_course import LeaveCourseInteractor
from learn_anything.course_platform.application.interactors.course.publish_course import PublishCourseInteractor
from learn_anything.course_platform.application.interactors.course.register_for_course import \
    RegisterForCourseInteractor
from learn_anything.course_platform.application.interactors.course.update_course import UpdateCourseInteractor
from learn_anything.course_platform.application.interactors.submission.create_submission import \
    CreateCodeTaskSubmissionInteractor, \
    CreatePollTaskSubmissionInteractor
from learn_anything.course_platform.application.interactors.submission.get_many_submissions import \
    GetActorSubmissionsInteractor, \
    GetTaskSubmissionsInteractor
from learn_anything.course_platform.application.interactors.task.create_task import CreateCodeTaskInteractor, \
    CreatePollTaskInteractor, \
    CreateTaskInteractor
from learn_anything.course_platform.application.interactors.task.delete_task import DeleteTaskInteractor
from learn_anything.course_platform.application.interactors.task.get_course_tasks import GetCourseTasksInteractor
from learn_anything.course_platform.application.interactors.task.update_code_task import UpdateCodeTaskInteractor, \
    UpdateCodeTaskTestInteractor, AddCodeTaskTestInteractor
from learn_anything.course_platform.application.interactors.task.update_task import UpdateTaskInteractor
from learn_anything.course_platform.application.ports.auth.auth_manager import AuthManager
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.auth.token import TokenProcessor
from learn_anything.course_platform.application.ports.committer import Commiter
from learn_anything.course_platform.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.course_platform.application.ports.data.course_gateway import CourseGateway, \
    RegistrationForCourseGateway
from learn_anything.course_platform.application.ports.data.file_manager import FileManager
from learn_anything.course_platform.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.course_platform.application.ports.data.task_gateway import TaskGateway
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.application.ports.playground import PlaygroundFactory
from learn_anything.course_platform.presentation.tg_bot.config import load_bot_config, BotConfig
from learn_anything.course_platform.presentation.web.config import load_web_config, WebConfig


DEFAULT_COURSE_PLATFORM_CONFIG_PATH = 'configs/course_platform.toml'


def gateways_provider() -> Provider:
    provider = Provider()

    provider.provide(UserMapper, scope=Scope.REQUEST, provides=UserGateway)
    provider.provide(AuthLinkMapper, scope=Scope.REQUEST, provides=AuthLinkGateway)
    provider.provide(CourseMapper, scope=Scope.REQUEST, provides=CourseGateway)
    provider.provide(RegistrationForCourseMapper, scope=Scope.REQUEST, provides=RegistrationForCourseGateway)
    provider.provide(TaskMapper, scope=Scope.REQUEST, provides=TaskGateway)
    provider.provide(SubmissionMapper, scope=Scope.REQUEST, provides=SubmissionGateway)

    provider.provide(SACommiter, scope=Scope.REQUEST, provides=Commiter)

    return provider


def infrastructure_provider() -> Provider:
    provider = Provider()

    provider.provide(TgB64TokenProcessor, scope=Scope.REQUEST, provides=TokenProcessor)
    provider.provide(S3FileManager, scope=Scope.REQUEST, provides=FileManager)
    provider.provide(UnixPlaygroundFactory, scope=Scope.REQUEST, provides=PlaygroundFactory)
    provider.provide(TelegramAuthManager, scope=Scope.REQUEST, provides=AuthManager)

    return provider


def interactors_provider() -> Provider:
    provider = Provider()

    provider.provide(LoginWithAuthLinkInteractor, scope=Scope.REQUEST)
    provider.provide(CreateAuthLinkInteractor, scope=Scope.REQUEST)
    provider.provide(InvalidateAuthLinkInteractor, scope=Scope.REQUEST)
    provider.provide(AuthenticateInteractor, scope=Scope.REQUEST)
    provider.provide(RegisterInteractor, scope=Scope.REQUEST)

    provider.provide(CreateCourseInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateCourseInteractor, scope=Scope.REQUEST)
    provider.provide(GetCourseInteractor, scope=Scope.REQUEST)
    provider.provide(GetCourseTasksInteractor, scope=Scope.REQUEST)
    provider.provide(GetAllCoursesInteractor, scope=Scope.REQUEST)
    provider.provide(GetActorCreatedCoursesInteractor, scope=Scope.REQUEST)
    provider.provide(GetActorRegisteredCoursesInteractor, scope=Scope.REQUEST)
    provider.provide(RegisterForCourseInteractor, scope=Scope.REQUEST)
    provider.provide(LeaveCourseInteractor, scope=Scope.REQUEST)
    provider.provide(PublishCourseInteractor, scope=Scope.REQUEST)
    provider.provide(DeleteCourseInteractor, scope=Scope.REQUEST)

    provider.provide(CreateTaskInteractor, scope=Scope.REQUEST)
    provider.provide(CreateCodeTaskInteractor, scope=Scope.REQUEST)
    provider.provide(CreatePollTaskInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateTaskInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateCodeTaskInteractor, scope=Scope.REQUEST)
    provider.provide(UpdateCodeTaskTestInteractor, scope=Scope.REQUEST)
    provider.provide(AddCodeTaskTestInteractor, scope=Scope.REQUEST)
    provider.provide(DeleteTaskInteractor, scope=Scope.REQUEST)

    provider.provide(CreateCodeTaskSubmissionInteractor, scope=Scope.REQUEST)
    provider.provide(CreatePollTaskSubmissionInteractor, scope=Scope.REQUEST)
    provider.provide(GetActorSubmissionsInteractor, scope=Scope.REQUEST)
    provider.provide(GetTaskSubmissionsInteractor, scope=Scope.REQUEST)

    return provider


def configs_provider() -> Provider:
    provider = Provider()

    cfg_path = os.getenv('COURSE_PLATFORM_CONFIG_PATH') or DEFAULT_COURSE_PLATFORM_CONFIG_PATH

    provider.provide(lambda: load_db_config(cfg_path), scope=Scope.APP, provides=DatabaseConfig)
    provider.provide(lambda: load_bot_config(cfg_path), scope=Scope.APP, provides=BotConfig)
    provider.provide(lambda: load_s3_config(cfg_path), scope=Scope.APP, provides=S3Config)
    provider.provide(lambda: load_redis_config(cfg_path), scope=Scope.APP, provides=RedisConfig)
    provider.provide(lambda: load_rmq_config(cfg_path), scope=Scope.APP, provides=RMQConfig)
    provider.provide(lambda: load_web_config(cfg_path), scope=Scope.APP, provides=WebConfig)

    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, obj: TelegramObject) -> int:
        return obj.from_user.id  # type: ignore[attr-defined, no-any-return, unused-ignore]

    @provide(scope=Scope.REQUEST)
    async def get_command(self, obj: TelegramObject) -> str | None:
        if not isinstance(obj, Message) or not obj.entities:
            return None

        for entity in obj.entities:
            if entity.type == MessageEntityType.BOT_COMMAND:
                return obj.text
        return None

    @provide(scope=Scope.REQUEST)
    async def get_identity_provider(
            self,
            user_id: int,
            user_gateway: UserGateway,
    ) -> IdentityProvider:
        identity_provider = TgIdentityProvider(
            user_id=user_id,
            user_gateway=user_gateway,
        )

        return identity_provider

    @provide(scope=Scope.APP)
    async def get_bot(
            self,
            bot_cfg: BotConfig,
    ) -> Bot:
        return Bot(token=bot_cfg.token)

    @provide(scope=Scope.APP)
    async def get_state_storage(self, redis_cfg: RedisConfig) -> RedisStorage:
        return RedisStorage.from_url(
            url=redis_cfg.dsn,
            json_dumps=partial(json.dumps, cls=DTOJSONEncoder),
            json_loads=partial(json.loads, object_hook=dto_obj_hook),
        )

    @provide(scope=Scope.APP)
    async def get_dp(
            self,
            storage: RedisStorage
    ) -> Dispatcher:
        dp = Dispatcher(
            events_isolation=SimpleEventIsolation(),
            storage=storage,
        )
        return dp


def db_provider() -> Provider:
    provider = Provider()

    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(get_async_session, scope=Scope.REQUEST)

    return provider


def rmq_provider() -> Provider:
    provider = Provider()

    provider.provide(get_connection_pool, provides=Pool[Connection], scope=Scope.APP)
    provider.provide(get_channel, provides=AbstractChannel, scope=Scope.REQUEST)

    return provider


def setup_providers() -> list[Provider]:
    providers = [
        gateways_provider(),
        infrastructure_provider(),
        db_provider(),
        rmq_provider(),
        configs_provider(),
        interactors_provider(),
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
