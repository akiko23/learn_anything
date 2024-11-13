import logging

from dataclasses import dataclass

from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.user.models import UserRole, UserID
from learn_anything.entities.user.rules import create_user


@dataclass
class AuthInputData:
    user_id: UserID
    fullname: str | None
    username: str | None
    token: str | None  # payload for defining role


@dataclass
class AuthOutputData:
    role: UserRole


class Authenticate:
    def __init__(self, user_gateway: UserGateway, committer: Commiter, id_provider: IdentityProvider):
        self._user_gateway = user_gateway
        self._id_provider = id_provider
        self._committer = committer

    async def execute(self, data: AuthInputData) -> AuthOutputData:
        role = await self._id_provider.get_role(token=data.token)
        user = create_user(
            user_id=data.user_id,
            fullname=data.fullname,
            username=data.username,
            role=role
        )

        await self._user_gateway.save(user)
        await self._committer.commit()

        logging.info("User %s was authenticated with role '%s'", data.user_id, role)

        return AuthOutputData(role=role)
