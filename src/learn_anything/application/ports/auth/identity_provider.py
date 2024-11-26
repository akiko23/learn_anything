from typing import Protocol

from learn_anything.entities.user.models import UserRole, UserID


class IdentityProvider(Protocol):
    async def get_current_user_id(self) -> UserID:
        raise NotImplementedError

    async def get_current_user_role(self) -> UserRole:
        raise NotImplementedError
