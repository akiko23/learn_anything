from typing import Sequence
from dataclasses import dataclass

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, AllCoursesCommonFilters, \
    AllCoursesForTeacherFilters
from learn_anything.entities.course.models import Course
from learn_anything.entities.user.errors import UserNotAuthenticatedError
from learn_anything.entities.user.models import UserRole


@dataclass
class GetAllCoursesInputData:
    pagination: Pagination
    filters: AllCoursesCommonFilters
    teacher_filters: AllCoursesForTeacherFilters


@dataclass
class GetAllCoursesOutputData:
    data: Sequence[Course]


class GetAllCoursesInteractor:
    def __init__(self, course_gateway: CourseGateway, id_provider: IdentityProvider):
        self._course_gateway = course_gateway
        self._id_provider = id_provider

    async def execute(self, data: GetAllCoursesInputData):
        actor = await self._id_provider.get_user()
        if not actor:
            raise UserNotAuthenticatedError

        if actor.role != UserRole.TEACHER:
            courses = await self._course_gateway.all_for_student(pagination=data.pagination, filters=data.filters)
        else:
            courses = await self._course_gateway.all_for_teacher(
                pagination=data.pagination,
                filters=data.filters,
                teacher_filters=data.teacher_filters
            )

        return GetAllCoursesOutputData(data=courses)
