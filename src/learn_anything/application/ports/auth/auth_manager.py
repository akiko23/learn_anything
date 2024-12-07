from typing import Protocol

from learn_anything.domain.user.enums import UserRole
from learn_anything.domain.user.models import UserID


class AuthManager(Protocol):
    async def login(self, username: str, password: str) -> (UserID, UserRole):
        raise NotImplementedError

    async def register(self, username: str | None, fullname: str, password: str, role: UserRole) -> UserID:
        raise NotImplementedError
