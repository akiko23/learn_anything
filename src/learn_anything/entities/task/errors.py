from dataclasses import dataclass

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.error import ApplicationError
from learn_anything.entities.task.models import TaskID, TaskType
from learn_anything.entities.user.models import UserID


@dataclass
class TaskDoesNotExistError(ApplicationError):
    task_id: TaskID

    @property
    def message(self) -> str:
        return f"Task with id={self.task_id} and does not exist"


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


@dataclass
class CodeTaskPreparedCodeIsInvalidError(ApplicationError):
    user_id: UserID
    code: str
    err: str

    @property
    def message(self):
        return f"""User {self.user_id} sent invalid task prepared code: 
'''
{self.code} 
'''
and got 
'''
{self.err}
'''"""

@dataclass
class CodeTaskTestCodeIsInvalidError(ApplicationError):
    user_id: UserID
    index: int
    code: str
    err: str

    @property
    def message(self):
        return f"""User {self.user_id} sent invalid code for the test #{self.index}: 
'''
{self.code} 
'''
and got:
'''
{self.err}
'''"""



# @dataclass
# class TaskCodeIsMaliciousError(ApplicationError):
#     user_id: UserID
#     code: str
#     err: str
#
#     @property
#     def message(self):
#         return f"""User {self.user_id} thinks he is cool. With this stupid task prepared code:
# '''
# {self.code}
# '''
#
# he tried to harm my server and got:
# '''
# {self.err}
# '''
# """
