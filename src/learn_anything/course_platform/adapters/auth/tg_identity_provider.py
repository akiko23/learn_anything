from aiogram.utils.deep_linking import encode_payload, decode_payload

from learn_anything.course_platform.adapters.auth.errors import TokenDecodeError
from learn_anything.course_platform.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.course_platform.application.ports.auth.token import TokenProcessor
from learn_anything.course_platform.application.ports.data.user_gateway import UserGateway
from learn_anything.course_platform.domain.entities.user.models import UserID, UserRole

THE_ONLY_OWNER_ID = 818525681


class TgB64TokenProcessor(TokenProcessor):
    def encode(self, subject: str) -> str:
        return encode_payload(subject)

    def decode(self, token: str) -> str:
        try:
            return decode_payload(token)
        except Exception:
            raise TokenDecodeError


class TgIdentityProvider(IdentityProvider):
    def __init__(
            self,
            user_id: int,
            user_gateway: UserGateway,
    ) -> None:
        self._user_id = user_id
        self._user_gateway = user_gateway

    @staticmethod
    def _parse_command_args(command: str | None) -> str | None:
        if command is None or len(command.split()) <= 1:
            return None

        args = command.split()
        return args[1]

    async def get_current_user_id(self) -> UserID:
        return UserID(self._user_id)

    async def get_current_user_role(self) -> UserRole | None:
        if self._user_id == THE_ONLY_OWNER_ID:
            return UserRole.BOT_OWNER

        user = await self._user_gateway.with_id(UserID(self._user_id))
        if user:
            return user.role

        return None
