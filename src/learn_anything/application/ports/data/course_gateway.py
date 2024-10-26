from dataclasses import dataclass
from typing import Protocol, Sequence

from learn_anything.application.input_data import Pagination
from learn_anything.entities.course.models import Course, CourseID, RegistrationForCourse
from learn_anything.entities.user.models import UserID, User


@dataclass(frozen=True)
class AllCoursesCommonFilters:
    actor_id: UserID
    author_id: UserID | None = None
    only_enrolled: bool | None = None
    only_not_enrolled: bool | None = None


@dataclass
class AllCoursesForTeacherFilters:
    only_created: bool | None = None
    only_not_created: bool | None = None


class CourseGateway(Protocol):
    async def with_id(self, course_id: CourseID) -> Course:
        raise NotImplementedError

    async def all_for_student(self, pagination: Pagination, filters: AllCoursesCommonFilters) -> Sequence[Course]:
        raise NotImplementedError

    async def all_for_teacher(
            self,
            pagination: Pagination,
            filters: AllCoursesCommonFilters,
            teacher_filters: AllCoursesForTeacherFilters,
    ) -> Sequence[Course]:
        raise NotImplementedError

    async def save(self, course: Course) -> CourseID:
        raise NotImplementedError


class RegistrationForCourseGateway(Protocol):
    async def read(self, user_id: UserID, course_id: CourseID) -> RegistrationForCourse:
        raise NotImplementedError

    async def exists(self, user_id: UserID, course_id: CourseID) -> bool:
        raise NotImplementedError

    async def save(self, registration: RegistrationForCourse) -> None:
        raise NotImplementedError
