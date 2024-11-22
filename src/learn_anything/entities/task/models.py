from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto

from typing import NewType, Sequence

from learn_anything.entities.course.models import CourseID

TaskID = NewType("TaskID", int)


class TaskType(StrEnum):
    THEORY = auto()
    CODE = auto()
    POLL = auto()
    TEXT_INPUT = auto()


class TaskDifficultyLevel(StrEnum):
    EASY = auto()
    MIDDLE = auto()
    HARD = auto()


@dataclass
class Task:
    id: TaskID | None
    type: TaskType
    topic: str | None
    title: str
    body: str
    course_id: CourseID
    # creator_id: UserID
    index_in_course: int
    created_at: datetime

@dataclass
class PracticeTask(Task):
    attempts_limit: int | None


@dataclass
class CodeTaskTest:
    code: str


@dataclass
class CodeTask(PracticeTask):
    prepared_code: str | None
    code_duration_timeout: int
    tests: Sequence[CodeTaskTest]


PollTaskOptionID = NewType('PollTaskOptionID', int)


@dataclass
class PollTaskOption:
    id: PollTaskOptionID | None
    content: str
    is_correct: bool

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplementedError
        return self.id == other.id


@dataclass
class PollTask(PracticeTask):
    options: Sequence[PollTaskOption]


@dataclass
class TextInputTaskAnswer:
    value: str

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplementedError
        return self.value.lower() == other.value.lower()


@dataclass
class TextInputTask(PracticeTask):
    correct_answers: Sequence[TextInputTaskAnswer]
