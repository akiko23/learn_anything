from dataclasses import dataclass
from enum import StrEnum, auto
from typing import NewType, Optional

UserID = NewType('UserID', int)


class UserRole(StrEnum):
    STUDENT = auto()
    TEACHER = auto()
    CURATOR = auto()


@dataclass(kw_only=True)
class User:
    id: UserID
    role: UserRole
    fullname: str
    username: Optional[str] = None
