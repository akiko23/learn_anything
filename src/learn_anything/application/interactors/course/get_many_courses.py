import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, GetManyCoursesFilters, \
    RegistrationForCourseGateway
from learn_anything.application.ports.data.file_manager import FileManager, COURSES_DEFAULT_DIRECTORY
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.course.models import CourseID


@dataclass
class GetManyCoursesInputData:
    pagination: Pagination
    filters: GetManyCoursesFilters | None = None


@dataclass
class CourseData:
    id: CourseID
    title: str
    description: str
    created_at: datetime
    creator: str
    total_registered: int
    photo_id: str | None
    photo_path: str | None
    user_is_registered: bool


@dataclass
class GetManyCoursesOutputData:
    courses: Sequence[CourseData]
    pagination: Pagination
    total: int


class GetAllCoursesInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetManyCoursesInputData) -> GetManyCoursesOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        courses, total = await self._course_gateway.all(
            pagination=data.pagination,
            filters=data.filters,
        )

        courses_output_data = []
        for course in courses:
            creator, registration = await asyncio.gather(
                self._user_gateway.with_id(course.creator_id),
                self._registration_for_course_gateway.read(user_id=actor_id, course_id=course.id)
            )

            course_data = CourseData(
                id=course.id,
                title=course.title,
                description=course.description,
                created_at=course.created_at,
                creator=creator.fullname,
                total_registered=course.total_registered,
                user_is_registered=registration is not None,
                photo_id=None,
                photo_path=None,
            )
            if course.photo_id:
                course_data.photo_id = course.photo_id
                course_data.photo_path = self._file_manager.generate_path(
                    directories=(COURSES_DEFAULT_DIRECTORY, ),
                    filename=course.photo_id,
                )

            courses_output_data.append(course_data)

        return GetManyCoursesOutputData(
            courses=courses_output_data,
            pagination=data.pagination,
            total=total,
        )


class GetActorCreatedCoursesInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetManyCoursesInputData) -> GetManyCoursesOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        data.filters.with_creator_id = actor_id

        courses, total = await self._course_gateway.all(
            pagination=data.pagination,
            filters=data.filters,
        )

        courses_output_data = []
        for course in courses:
            creator, registration = await asyncio.gather(
                self._user_gateway.with_id(course.creator_id),
                self._registration_for_course_gateway.read(user_id=actor_id, course_id=course.id)
            )

            course_data = CourseData(
                id=course.id,
                title=course.title,
                description=course.description,
                created_at=course.created_at,
                creator=creator.fullname,
                total_registered=course.total_registered,
                user_is_registered=registration is not None,
                photo_id=None,
                photo_path=None,
            )
            if course.photo_id:
                course_data.photo_id = course.photo_id
                course_data.photo_path = self._file_manager.generate_path(
                    directories=(COURSES_DEFAULT_DIRECTORY, ),
                    filename=course.photo_id,
                )

            courses_output_data.append(course_data)

        return GetManyCoursesOutputData(
            courses=courses_output_data,
            pagination=data.pagination,
            total=total,
        )


class GetActorRegisteredCoursesInteractor:
    def __init__(
            self,
            course_gateway: CourseGateway,
            registration_for_course_gateway: RegistrationForCourseGateway,
            user_gateway: UserGateway,
            file_manager: FileManager,
            id_provider: IdentityProvider
    ) -> None:
        self._course_gateway = course_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._user_gateway = user_gateway
        self._file_manager = file_manager
        self._id_provider = id_provider

    async def execute(self, data: GetManyCoursesInputData) -> GetManyCoursesOutputData:
        actor_id = await self._id_provider.get_current_user_id()

        data.filters.with_registered_actor_id = actor_id

        courses, total = await self._course_gateway.all(
            pagination=data.pagination,
            filters=data.filters,
        )

        courses_output_data = []
        for course in courses:
            creator, registration = await asyncio.gather(
                self._user_gateway.with_id(course.creator_id),
                self._registration_for_course_gateway.read(user_id=actor_id, course_id=course.id)
            )

            course_data = CourseData(
                id=course.id,
                title=course.title,
                description=course.description,
                created_at=course.created_at,
                creator=creator.fullname,
                total_registered=course.total_registered,
                user_is_registered=registration is not None,
                photo_id=None,
                photo_path=None,
            )
            if course.photo_id:
                course_data.photo_id = course.photo_id
                course_data.photo_path = self._file_manager.generate_path(
                    directories=(COURSES_DEFAULT_DIRECTORY, ),
                    filename=course.photo_id,
                )

            courses_output_data.append(course_data)

        return GetManyCoursesOutputData(
            courses=courses_output_data,
            pagination=data.pagination,
            total=total,
        )
