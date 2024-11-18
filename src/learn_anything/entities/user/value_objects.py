from dataclasses import dataclass
from datetime import datetime

from learn_anything.entities.user.errors import UsernameToShortError, RoleUnavailableForAuthError, InvalidExpiresAtError
from learn_anything.entities.user.models import UserRole


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
            raise RoleUnavailableForAuthError(self.value)


@dataclass
class ExpiresAt:
    value: str

    def __post_init__(self):
        self.value: datetime = datetime.strptime(self.value, '%d-%m-%Y')
        if self.value < datetime.now():
            raise InvalidExpiresAtError(self.value)
