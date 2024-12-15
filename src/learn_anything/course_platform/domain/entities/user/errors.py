import uuid
from dataclasses import dataclass

from learn_anything.course_platform.domain.error import ApplicationError
from learn_anything.course_platform.domain.entities.user.models import UserRole


@dataclass
class AuthLinkCreationForbiddenError(ApplicationError):
    role: UserRole

    @property
    def message(self) -> str:
        return f"Only bot owner can create auth links. Your role: {self.role}."


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
