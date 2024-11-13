from dataclasses import dataclass

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.error import ApplicationError
from learn_anything.entities.task.models import TaskID, TaskType
from learn_anything.entities.user.models import UserID


@dataclass
class TaskDoesNotExistError(ApplicationError):
    task_id: TaskID
    type: TaskType

    @property
    def message(self) -> str:
        return f"{self.type.title()} task with id={self.task_id} and does not exist"


@dataclass
class ActorIsNotRegisteredOnCourseError(ApplicationError):
    actor_id: UserID
    course_id: CourseID

    @property
    def message(self) -> str:
        return f'User {self.actor_id} is not registered for course {self.course_id}'


@dataclass
class CanNotSendSubmissionToNonPublishedCourse(ApplicationError):
    course_id: CourseID

    @property
    def message(self):
        return "Can not send a submission to non published course task"


@dataclass
class AttemptsLimitExceededForTaskError(ApplicationError):
    task_id: TaskID

    @property
    def message(self):
        return f"Attempts limit for task {self.task_id} was already reached"
