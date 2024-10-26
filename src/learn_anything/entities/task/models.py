from dataclasses import dataclass

from typing import NewType

from learn_anything.entities.user.models import UserID

TaskID = NewType("TaskID", int)

@dataclass
class Task:
    pass



@dataclass(frozen=True)
class PracticeTask:
    lesson_id: TaskID
    number: int
    title: str
    description: str


class Submission:
    student_id: UserID
    code: str
    task_id: TaskID
