from learn_anything.course_platform.adapters.auth.errors import UserDoesNotExistError
from learn_anything.course_platform.application.ports.auth.auth_manager import AuthManager
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.domain.entities.user.models import UserID, User


class TelegramAuthManager(AuthManager):
    def __init__(
            self,
            user_gateway: UserGateway,
            identity_provider: IdentityProvider
    ):
        self._user_gateway = user_gateway
        self._identity_provider = identity_provider

    async def login(self, username: str, password: str) -> tuple[UserID, UserRole]:
        user = await self._user_gateway.with_username(username=username)
        if not user:
            raise UserDoesNotExistError
        return user.id, user.role

    async def register(self, username: str | None, fullname: str, password: str, role: UserRole) -> UserID:
        user_id = await self._identity_provider.get_current_user_id()
        await self._user_gateway.save(
            User(
                id=user_id,
                role=role,
                fullname=fullname,
                username=username,
            )
        )
        return user_id
