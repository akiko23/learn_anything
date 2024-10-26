from abc import abstractmethod
from typing import Protocol

from learn_anything.entities.user.models import User, UserRole


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_role(self) -> UserRole | None:
        raise NotImplementedError
