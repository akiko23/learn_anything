from datetime import datetime
from typing import Sequence
from dataclasses import dataclass

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, GetManyCoursesFilters, \
    RegistrationForCourseGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.models import CourseID


@dataclass
class GetManyCoursesInputData:
    pagination: Pagination
    filters: GetManyCoursesFilters | None = None


@dataclass
class CoursePartialData:
    id: CourseID
    title: str
    description: str
    created_at: datetime
    creator: str
    total_registered: int


@dataclass
class GetManyCoursesOutputData:
    courses: Sequence[CoursePartialData]
    pagination: Pagination
    total: int


class GetManyCoursesInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._id_provider = id_provider

    async def execute(self, data: GetManyCoursesInputData) -> GetManyCoursesOutputData:
        courses, total = await self._course_gateway.all(
            pagination=data.pagination,
            filters=data.filters,
        )
        print('Loaded courses:', courses)

        courses_output_data = []
        for course in courses:
            creator = await self._user_gateway.with_id(course.creator_id)
            courses_output_data.append(
                CoursePartialData(
                    id=course.id,
                    title=course.title,
                    description=course.description,
                    created_at=course.created_at,
                    creator=creator.fullname,
                    total_registered=course.total_registered,
                )
            )

        return GetManyCoursesOutputData(
            courses=courses_output_data,
            pagination=data.pagination,
            total=total,
        )


