from uuid import UUID

from aiogram.utils.deep_linking import encode_payload, decode_payload
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.auth.token import TokenProcessor
from learn_anything.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.user.errors import UserNotAuthenticatedError, InvalidAuthLinkError
from learn_anything.entities.user.models import User, UserID, UserRole


class TgB64TokenProcessor(TokenProcessor):
    def encode(self, subject: str) -> str:
        return encode_payload(subject)

    def decode(self, token: str) -> str:
        return decode_payload(token)


class TgIdentityProvider(IdentityProvider):
    def __init__(
            self,
            user_id: int,
            user_gateway: UserGateway,
            auth_link_gateway: AuthLinkGateway,
            token_processor: TokenProcessor,
    ) -> None:
        self._user_id = user_id
        self._user_gateway = user_gateway
        self._auth_link_gateway = auth_link_gateway
        self._token_processor = token_processor

    async def get_user(self) -> User:
        user = await self._user_gateway.with_id(UserID(self._user_id))
        if not user:
            raise UserNotAuthenticatedError

        return user

    async def get_role(self, token: str | None = None) -> UserRole:
        if self._user_id == 818525681:
            return UserRole.BOT_OWNER

        if token:
            auth_link_id = self._token_processor.decode(token)
            return await self._get_role_by_auth_link_id(auth_link_id)

        user = await self._user_gateway.with_id(UserID(self._user_id))
        if user:
            return user.role

        return UserRole.STUDENT

    async def _get_role_by_auth_link_id(self, auth_link_id: str):
        auth_link_id = UUID(auth_link_id)

        auth_link = await self._auth_link_gateway.with_id(auth_link_id)
        if auth_link.is_invalid:
            await self._auth_link_gateway.delete(auth_link_id)
            raise InvalidAuthLinkError

        auth_link.usages -= 1
        await self._auth_link_gateway.save(auth_link)

        return auth_link.for_role
