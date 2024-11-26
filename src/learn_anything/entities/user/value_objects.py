from dataclasses import dataclass
from datetime import datetime

from learn_anything.entities.user.enums import UserRole
from learn_anything.entities.user.errors import UsernameToShortError, RoleIsUnavailableForAuthError, InvalidExpiresAtError


@dataclass
class Username:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) <= 5:
            raise UsernameToShortError(self.value)


@dataclass
class AvailableForAuthRole:
    value: UserRole

    def __post_init__(self):
        if self.value not in (UserRole.MODERATOR, UserRole.MENTOR):
            raise RoleIsUnavailableForAuthError(self.value)


@dataclass
class ExpiresAt:
    value: datetime

    def __post_init__(self):
        if self.value < datetime.now():
            raise InvalidExpiresAtError(self.value)
