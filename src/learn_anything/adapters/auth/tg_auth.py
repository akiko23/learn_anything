from uuid import UUID

from aiogram.utils.deep_linking import encode_payload, decode_payload

from learn_anything.adapters.auth.errors import TokenDecodeError
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.auth.token import TokenProcessor
from learn_anything.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.user.errors import InvalidAuthLinkError
from learn_anything.entities.user.models import UserID, UserRole

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
            command: str | None,
            user_gateway: UserGateway,
            auth_link_gateway: AuthLinkGateway,
            token_processor: TokenProcessor,
    ) -> None:
        self._user_id = user_id
        self._token: str | None = self._parse_command_args(command)
        self._user_gateway = user_gateway
        self._auth_link_gateway = auth_link_gateway
        self._token_processor = token_processor

    @staticmethod
    def _parse_command_args(command: str | None) -> str | None:
        if command is None or len(command.split()) <= 1:
            return None

        args = command.split()
        return args[1]

    async def get_current_user_id(self) -> UserID:
        return UserID(self._user_id)

    async def get_current_user_role(self) -> UserRole:
        if self._user_id == THE_ONLY_OWNER_ID:
            return UserRole.BOT_OWNER

        if self._token:
            auth_link_id = self._token_processor.decode(self._token)
            auth_link_id = UUID(auth_link_id)

            auth_link = await self._auth_link_gateway.with_id(auth_link_id)
            if auth_link.is_invalid:
                await self._auth_link_gateway.delete(auth_link_id)
                raise InvalidAuthLinkError

            auth_link.usages -= 1
            await self._auth_link_gateway.save(auth_link)

            return auth_link.for_role

        user = await self._user_gateway.with_id(UserID(self._user_id))
        if user:
            return user.role

        return UserRole.STUDENT
