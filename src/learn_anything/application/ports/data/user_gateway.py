from typing import Protocol

from learn_anything.domain.entities.user.models import User, UserID


class UserGateway(Protocol):
    async def with_id(self, user_id: UserID) -> User | None:
        raise NotImplementedError

    async def with_username(self, username: str) -> User | None:
        raise NotImplementedError

    async def save(self, user: User) -> None:
        raise NotImplementedError
