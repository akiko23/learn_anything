from abc import abstractmethod
from typing import Protocol

from learn_anything.entities.user.models import User, UserRole


class IdentityProvider(Protocol):
    async def get_user(self) -> User:
        raise NotImplementedError

    async def get_role(self) -> UserRole:
        raise NotImplementedError
