from typing import Protocol

from learn_anything.entities.user.models import User, UserID, AuthLink


class UserGateway(Protocol):
    async def with_id(self, user_id: UserID) -> User:
        raise NotImplementedError

    async def save(self, user: User) -> None:
        raise NotImplementedError

    async def exists(self, user_id: UserID) -> bool:
        raise NotImplementedError

