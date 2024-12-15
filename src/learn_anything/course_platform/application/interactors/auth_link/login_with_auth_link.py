import logging
from dataclasses import dataclass
from uuid import UUID

from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.auth.token import TokenProcessor
from learn_anything.course_platform.application.ports.committer import Commiter
from learn_anything.course_platform.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.domain.entities.user.errors import InvalidAuthLinkError
from learn_anything.course_platform.domain.entities.user.models import UserRole, UserID
from learn_anything.course_platform.domain.entities.user.rules import create_user

logger = logging.getLogger(__name__)


@dataclass
class LoginWithAuthLinkInputData:
    user_id: UserID
    fullname: str | None
    username: str | None
    auth_token: str


@dataclass
class LoginWithAuthLinkOutputData:
    role: UserRole
    is_newbie: bool


class LoginWithAuthLinkInteractor:
    def __init__(
            self,
            user_gateway: UserGateway,
            auth_link_gateway: AuthLinkGateway,
            committer: Commiter,
            id_provider: IdentityProvider,
            token_processor: TokenProcessor,
    ):
        self._user_gateway = user_gateway
        self._auth_link_gateway = auth_link_gateway
        self._id_provider = id_provider
        self._token_processor = token_processor
        self._committer = committer

    async def execute(self, data: LoginWithAuthLinkInputData) -> LoginWithAuthLinkOutputData:
        is_newbie = False
        role = await self._id_provider.get_current_user_role()
        if role is None:
            is_newbie = True

        auth_link_id = self._token_processor.decode(data.auth_token)
        auth_link_id = UUID(auth_link_id)

        auth_link = await self._auth_link_gateway.with_id(auth_link_id)
        if auth_link.is_invalid:
            await self._auth_link_gateway.delete(auth_link_id)
            raise InvalidAuthLinkError

        auth_link.usages -= 1
        await self._auth_link_gateway.save(auth_link)

        role = auth_link.for_role
        user = create_user(
            user_id=data.user_id,
            fullname=data.fullname,
            username=data.username,
            role=role
        )

        await self._user_gateway.save(user)
        await self._committer.commit()

        logger.info("User %s was authenticated via link and got role '%s'", data.user_id, role)

        return LoginWithAuthLinkOutputData(role=role, is_newbie=is_newbie)
