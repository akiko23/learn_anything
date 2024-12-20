import logging
from dataclasses import dataclass

from learn_anything.course_platform.application.ports.auth.auth_manager import AuthManager
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.committer import Commiter
from learn_anything.course_platform.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.domain.entities.user.models import UserID

logger = logging.getLogger(__name__)


@dataclass
class RegisterInputData:
    username: str | None
    fullname: str
    password: str


@dataclass
class RegisterOutputData:
    user_id: UserID
    role: UserRole


DEFAULT_ROLE = UserRole.STUDENT


class RegisterInteractor:
    def __init__(
            self,
            user_gateway: UserGateway,
            auth_link_gateway: AuthLinkGateway,
            committer: Commiter,
            id_provider: IdentityProvider,
            auth_manager: AuthManager,
    ):
        self._user_gateway = user_gateway
        self._auth_link_gateway = auth_link_gateway
        self._id_provider = id_provider
        self._auth_manager = auth_manager
        self._committer = committer

    async def execute(self, data: RegisterInputData) -> RegisterOutputData:
        role = DEFAULT_ROLE
        user_id = await self._auth_manager.register(
            username=data.username,
            fullname=data.fullname,
            password=data.password,
            role=role
        )

        await self._committer.commit()

        logger.info("User %s with role '%s' was just registered", user_id, role)

        return RegisterOutputData(user_id=user_id, role=role)
