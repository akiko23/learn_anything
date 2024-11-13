from dataclasses import dataclass
from datetime import datetime

from learn_anything.entities.task.models import PollTaskOptionID, TaskID
from learn_anything.entities.user.models import UserID


@dataclass
class Submission:
    user_id: UserID
    task_id: TaskID
    attempt_number: int
    is_correct: bool
    created_at: datetime


@dataclass
class CodeSubmission(Submission):
    code: str


@dataclass
class PollSubmission(Submission):
    selected_option: PollTaskOptionID


@dataclass
class TextInputSubmission(Submission):
    answer: str
