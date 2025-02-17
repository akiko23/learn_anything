import uuid
from dataclasses import dataclass

from learn_anything.course_platform.application.errors import UserNotAuthenticatedError
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.domain.entities.user.errors import AuthLinkCreationForbiddenError, \
    AuthLinkDoesNotExist


@dataclass
class InvalidateAuthLinkInputData:
    link_id: uuid.UUID


class InvalidateAuthLinkInteractor:
    def __init__(
            self,
            auth_link_gateway: AuthLinkGateway,
            id_provider: IdentityProvider
    ) -> None:
        self._auth_link_gateway = auth_link_gateway
        self._id_provider = id_provider

    async def execute(self, data: InvalidateAuthLinkInputData) -> None:
        actor_role = await self._id_provider.get_current_user_role()
        if not actor_role:
            raise UserNotAuthenticatedError()

        if actor_role != UserRole.BOT_OWNER:
            raise AuthLinkCreationForbiddenError(actor_role)

        auth_link = await self._auth_link_gateway.with_id(data.link_id)
        if not auth_link:
            raise AuthLinkDoesNotExist(data.link_id)

        await self._auth_link_gateway.delete(data.link_id)
