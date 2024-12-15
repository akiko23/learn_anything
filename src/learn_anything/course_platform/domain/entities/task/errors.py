from dataclasses import dataclass
from typing import Union

from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.domain.error import ApplicationError
from learn_anything.course_platform.domain.entities.task.models import TaskID, PollTaskOptionID
from learn_anything.course_platform.domain.entities.user.models import UserID


@dataclass
class TaskDoesNotExistError(ApplicationError):
    task_id: TaskID

    @property
    def message(self) -> str:
        return f"Task with id={self.task_id} does not exist"


@dataclass
class ActorIsNotRegisteredOnCourseError(ApplicationError):
    course_id: CourseID

    @property
    def message(self) -> str:
        return f'You are not registered for course {self.course_id} so you can not create submission'


@dataclass
class AttemptsLimitReachedForTaskError(ApplicationError):
    task_id: TaskID

    @property
    def message(self):
        return f"Attempts limit for task {self.task_id} was already reached"


@dataclass
class TaskPreparedCodeIsInvalidError(ApplicationError):
    code: str
    err: str

    @property
    def message(self):
        return f"Invalid task prepared code. Stderr: {self.err}"


@dataclass
class TaskTestCodeIsInvalidError(ApplicationError):
    user_id: UserID
    index: int
    code: str
    err: str

    @property
    def message(self):
        return f"Invalid code for the test #{self.index}. Stderr:\n\n{self.err}"


InvalidTaskCodeError = Union[TaskTestCodeIsInvalidError, TaskPreparedCodeIsInvalidError]


@dataclass
class PollTaskOptionDoesNotExistError(ApplicationError):
    option_id: PollTaskOptionID

    @property
    def message(self) -> str:
        return f"Poll task option with id={self.option_id} does not exist"


@dataclass
class TheoryTaskHasNoSubmissionsError(ApplicationError):
    task_id: TaskID

    @property
    def message(self) -> str:
        return f"Theory task with id={self.task_id} can't have submissions"


@dataclass
class CodeTaskTestAlreadyExistsError(ApplicationError):
    task_id: TaskID
    code: str

    @property
    def message(self) -> str:
        return f"Test for task={self.task_id} with code={self.code} already exists"

