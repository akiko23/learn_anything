import uuid
from typing import Protocol

from learn_anything.domain.entities.user.models import AuthLink


class AuthLinkGateway(Protocol):
    async def save(self, auth_link: AuthLink) -> uuid.UUID:
        raise NotImplementedError

    async def with_id(self, link_id: uuid.UUID) -> AuthLink:
        raise NotImplementedError

    async def delete(self, auth_link_id: uuid.UUID) -> None:
        raise NotImplementedError
