from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Protocol, Sequence

from learn_anything.application.input_data import Pagination
from learn_anything.entities.course.models import Course, CourseID, RegistrationForCourse, CourseShareRule
from learn_anything.entities.user.models import UserID


class SortBy(StrEnum):
    POPULARITY = auto()
    DATE = auto()
    LAST_UPDATE = auto()
    LAST_SUBMISSION = auto()


@dataclass
class GetManyCoursesFilters:
    ### public filters
    sort_by: SortBy
    author_name: str | None = None
    title: str | None = None
    ###

    # if you want to get only courses where actor registered in
    with_registered_actor_id: UserID | None = None

    # if you want to get only courses which actor has created
    with_creator_id: UserID | None = None


@dataclass
class GetCoursesActorCreatedFilters:
    title: str | None = None
    sort_by: SortBy = SortBy.DATE


class CourseGateway(Protocol):
    async def with_id(self, course_id: CourseID) -> Course:
        raise NotImplementedError

    async def with_creator(
            self,
            user_id: UserID,
            pagination: Pagination,
            filters: GetCoursesActorCreatedFilters,
    ) -> (Sequence[Course], int):
        raise NotImplementedError

    # todo: rewrite this (srp violation)
    async def all(
            self,
            pagination: Pagination,
            filters: GetManyCoursesFilters,
    ) -> (Sequence[Course], int):
        raise NotImplementedError

    async def save(self, course: Course) -> CourseID:
        raise NotImplementedError

    async def delete(self, course_id: CourseID) -> None:
        raise NotImplementedError

    async def get_share_rules(self, course_id: CourseID) -> Sequence[CourseShareRule]:
        raise NotImplementedError

    async def add_share_rule(self, share_rule: CourseShareRule) -> None:
        raise NotImplementedError

    async def delete_share_rule(self, course_id: CourseID, user_id: UserID) -> None:
        raise NotImplementedError


class RegistrationForCourseGateway(Protocol):
    async def read(self, user_id: UserID, course_id: CourseID) -> RegistrationForCourse | None:
        raise NotImplementedError

    async def save(self, registration: RegistrationForCourse) -> None:
        raise NotImplementedError

    async def delete(self, user_id: UserID, course_id: CourseID) -> None:
        raise NotImplementedError
