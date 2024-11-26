import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import NewType, Optional

from learn_anything.entities.user.enums import UserRole
from learn_anything.entities.user.value_objects import AvailableForAuthRole, ExpiresAt

UserID = NewType('UserID', int)


@dataclass(kw_only=True)
class User:
    id: UserID
    role: UserRole
    fullname: str | None
    username: Optional[str] = None


@dataclass
class AuthLink:
    id: uuid.UUID | None
    usages: int
    for_role: UserRole
    expires_at: datetime

    @property
    def is_invalid(self):
        return self.usages <= 0 or self.expires_at < datetime.now()
