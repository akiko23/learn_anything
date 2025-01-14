from typing import Protocol

from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.domain.entities.user.models import UserID


class IdentityProvider(Protocol):
    async def get_current_user_id(self) -> UserID:
        raise NotImplementedError

    async def get_current_user_role(self) -> UserRole | None:
        raise NotImplementedError
