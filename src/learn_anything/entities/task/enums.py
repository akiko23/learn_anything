from enum import auto, StrEnum


class TaskType(StrEnum):
    THEORY = auto()
    CODE = auto()
    POLL = auto()
    TEXT_INPUT = auto()


class TaskDifficultyLevel(StrEnum):
    EASY = auto()
    MIDDLE = auto()
    HARD = auto()