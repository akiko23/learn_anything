from dataclasses import dataclass
from datetime import datetime

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.auth.token import TokenProcessor
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.domain.entities.user.errors import AuthLinkCreationForbiddenError
from learn_anything.domain.entities.user.models import UserRole
from learn_anything.domain.entities.user.rules import create_auth_link


@dataclass
class CreateAuthLinkInputData:
    for_role: UserRole
    usages: int
    expires_at: datetime


@dataclass
class CreateAuthLinkOutputData:
    token: str


class CreateAuthLinkInteractor:
    def __init__(
            self,
            auth_link_gateway: AuthLinkGateway,
            commiter: Commiter,
            token_processor: TokenProcessor,
            id_provider: IdentityProvider
    ) -> None:
        self._auth_link_gateway = auth_link_gateway
        self._commiter = commiter
        self._token_processor = token_processor
        self._id_provider = id_provider

    async def execute(self, data: CreateAuthLinkInputData) -> CreateAuthLinkOutputData:
        actor_role = await self._id_provider.get_current_user_role()
        if actor_role != UserRole.BOT_OWNER:
            raise AuthLinkCreationForbiddenError(actor_role)

        auth_link = create_auth_link(
            link_id=None,
            for_role=data.for_role,
            usages=data.usages,
            expires_at=data.expires_at,
        )
        new_auth_link_id = await self._auth_link_gateway.save(auth_link)

        await self._commiter.commit()

        token = self._token_processor.encode(subject=str(new_auth_link_id))
        return CreateAuthLinkOutputData(token=token)
