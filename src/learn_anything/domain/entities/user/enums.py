from enum import StrEnum, auto


class UserRole(StrEnum):
    STUDENT = auto()
    MENTOR = auto()
    MODERATOR = auto()
    BOT_OWNER = auto()

