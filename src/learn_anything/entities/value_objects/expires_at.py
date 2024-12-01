from dataclasses import dataclass
from datetime import datetime

from learn_anything.entities.error import ApplicationError


@dataclass
class InvalidExpiresAtError(ApplicationError):
    expires_at: datetime

    @property
    def message(self) -> str:
        return f"Expires_at={self.expires_at} can not be earlier than now."


@dataclass
class ExpiresAt:
    value: datetime

    def __post_init__(self):
        if self.value < datetime.now():
            raise InvalidExpiresAtError(self.value)
