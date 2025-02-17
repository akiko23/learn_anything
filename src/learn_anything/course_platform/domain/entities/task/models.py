from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Sequence, Any

from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.domain.entities.task.enums import TaskType

TaskID = NewType("TaskID", int)


@dataclass
class Task:
    id: TaskID
    type: TaskType
    topic: str | None
    title: str
    body: str
    course_id: CourseID
    # creator_id: UserID
    index_in_course: int
    created_at: datetime
    updated_at: datetime


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
    tests: list[CodeTaskTest]


PollTaskOptionID = NewType('PollTaskOptionID', int)


@dataclass
class PollTaskOption:
    id: PollTaskOptionID | None
    content: str
    is_correct: bool

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            raise NotImplementedError
        return self.id == other.id


@dataclass
class PollTask(PracticeTask):
    options: Sequence[PollTaskOption]


@dataclass
class TextInputTaskAnswer:
    value: str

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            raise NotImplementedError
        return self.value.lower() == other.value.lower()


@dataclass
class TextInputTask(PracticeTask):
    correct_answers: Sequence[TextInputTaskAnswer]
