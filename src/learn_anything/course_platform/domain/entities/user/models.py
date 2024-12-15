import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from learn_anything.course_platform.domain.entities.user.enums import UserRole

UserID = NewType('UserID', int)


@dataclass(kw_only=True)
class User:
    id: UserID
    role: UserRole
    fullname: str | None
    username: str | None


@dataclass
class AuthLink:
    id: uuid.UUID | None
    usages: int
    for_role: UserRole
    expires_at: datetime

    @property
    def is_invalid(self):
        return self.usages <= 0 or self.expires_at < datetime.now()
