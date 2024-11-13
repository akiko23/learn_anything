import uuid
from dataclasses import dataclass
from datetime import datetime

from learn_anything.entities.error import ApplicationError
from learn_anything.entities.user.models import UserID, UserRole


class UserNotAuthenticatedError(Exception):
    message: str = "User not authenticated"


@dataclass
class UsernameToShortError(ApplicationError):
    username: str

    @property
    def message(self):
        return f"""Username={self.username} is too short.
                Username length must be at least 5 characters"""


@dataclass
class UserAlreadyExistError(ApplicationError):
    user_id: UserID

    @property
    def message(self):
        return f"User with id={self.user_id} already exists."


@dataclass
class AuthLinkCreationForbiddenError(ApplicationError):
    role: UserRole

    @property
    def message(self) -> str:
        return f"Only bot owner can create auth links. Your role: {self.role}."


@dataclass
class RoleUnavailableForAuthError(ApplicationError):
    role: UserRole

    @property
    def message(self) -> str:
        return f"Role '{self.role}' is unavailable for auth."


@dataclass
class InvalidExpiresAtError(ApplicationError):
    expires_at: datetime

    @property
    def message(self) -> str:
        return f"Expires_at={self.expires_at} can not be earlier than now."


@dataclass
class AuthLinkDoesNotExist(ApplicationError):
    link_id: uuid.UUID

    @property
    def message(self) -> str:
        return f"Auth link with id={self.link_id} does not exist."


class InvalidAuthLinkError(ApplicationError):
    @property
    def message(self) -> str:
        return "Invalid auth link."
