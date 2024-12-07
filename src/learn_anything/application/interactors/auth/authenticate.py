import logging
from dataclasses import dataclass

from learn_anything.application.ports.auth.auth_manager import AuthManager
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.domain.entities.user.models import UserRole, UserID


@dataclass
class AuthInputData:
    username: str | None
    password: str


@dataclass
class AuthOutputData:
    user_id: UserID
    role: UserRole


class AuthenticateInteractor:
    def __init__(
            self,
            user_gateway: UserGateway,
            committer: Commiter,
            id_provider: IdentityProvider,
            auth_manager: AuthManager,
    ):
        self._user_gateway = user_gateway
        self._id_provider = id_provider
        self._auth_manager = auth_manager
        self._committer = committer

    async def execute(self, data: AuthInputData) -> AuthOutputData:
        # check the cache
        user_id = await self._id_provider.get_current_user_id()
        role = await self._id_provider.get_current_user_role()
        if role and user_id:
            return AuthOutputData(user_id=user_id, role=role)

        user_id, user_role = await self._auth_manager.login(username=data.username, password=data.password)

        logging.info("User %s with role '%s' was authenticated", user_id, user_role)

        return AuthOutputData(user_id=user_id, role=user_role)
