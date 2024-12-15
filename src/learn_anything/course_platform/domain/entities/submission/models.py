from dataclasses import dataclass
from datetime import datetime

from learn_anything.course_platform.domain.entities.task.models import TaskID, PollTaskOption
from learn_anything.course_platform.domain.entities.user.models import UserID


@dataclass
class Submission:
    user_id: UserID
    task_id: TaskID
    is_correct: bool
    created_at: datetime


@dataclass
class CodeSubmission(Submission):
    code: str


@dataclass
class PollSubmission(Submission):
    selected_option: PollTaskOption


@dataclass
class TextInputSubmission(Submission):
    answer: str
