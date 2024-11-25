from dataclasses import dataclass
from typing import Union

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.error import ApplicationError
from learn_anything.entities.task.models import TaskID
from learn_anything.entities.user.models import UserID


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
        return f"Invalid code for the test #{self.index}. Stderr: {self.err}"


InvalidCodeError = Union[TaskTestCodeIsInvalidError, TaskPreparedCodeIsInvalidError]
