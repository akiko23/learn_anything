from dataclasses import dataclass
from typing import Any

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.error import ApplicationError
from learn_anything.entities.user.models import UserRole, UserID


@dataclass
class CourseCreationForbiddenError(ApplicationError):
    role: UserRole

    @property
    def message(self) -> str:
        return f'Only teachers can create courses. Your role: "{self.role}"'


@dataclass
class CourseDoesNotExistError(ApplicationError):
    course_id: Any

    @property
    def message(self) -> str:
        return f'Course with provided id="{self.course_id}" does not exist'


@dataclass
class UserAlreadyRegisteredForCourseError(ApplicationError):
    user_id: UserID
    course_id: CourseID

    @property
    def message(self) -> str:
        return f'User {self.user_id} already registered for course {self.course_id}'


class NoAccessToCourseError(ApplicationError):
    message: str = 'Only course creator has access to his course'


@dataclass
class RegistrationsLimitExceededError(ApplicationError):
    course_id: CourseID

    @property
    def message(self) -> str:
        return f'Registrations limit for course {self.course_id} already reached.'


class CoursePermissionError:
    message: str = "You don't have write access to this course"
