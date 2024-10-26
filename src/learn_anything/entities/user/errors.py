from dataclasses import dataclass

from learn_anything.entities.error import ApplicationError
from learn_anything.entities.user.models import UserID


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
