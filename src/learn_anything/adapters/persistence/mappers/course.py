import asyncio
from typing import Sequence

from sqlalchemy import select, exists, func, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Bundle

from learn_anything.application.input_data import Pagination
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway, \
    GetManyCoursesFilters, SortBy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, not_

from learn_anything.entities.course.models import Course, CourseID, RegistrationForCourse, CourseShareRule
from learn_anything.entities.user.models import UserID
from learn_anything.adapters.persistence.tables.course import courses_table, registrations_for_courses_table, \
    course_share_rules_table
from learn_anything.adapters.persistence.tables.user import users_table


class CourseMapper(CourseGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def with_id(self, course_id: CourseID) -> Course:
        course_total_registrations = (
            select(
                courses_table.c.id,
                func.count(registrations_for_courses_table.c.user_id).label("total_registered")
            ).
            outerjoin(target=registrations_for_courses_table).
            group_by(courses_table.c.id).
            having(courses_table.c.id == course_id).
            cte('course_total_registrations')
        )

        stmt = (
            select(
                Bundle("course", *courses_table.c),
                Bundle("course_total_registrations", course_total_registrations.c.total_registered),
            ).
            add_cte(course_total_registrations).
            select_from(courses_table).
            join(course_total_registrations, onclause=courses_table.c.id == course_total_registrations.c.id)
        )

        res = await self._session.execute(stmt)

        row = res.fetchone()
        return Course(
            **row.course._mapping,  # noqa
            total_registered=row.course_total_registrations.total_registered,
        )


    async def all(
            self,
            pagination: Pagination,
            filters: GetManyCoursesFilters,
    ) -> (Sequence[Course], int):
        course_total_registrations = (
            select(
                courses_table.c.id,
                func.count(registrations_for_courses_table.c.user_id).label("total_registered")
            ).
            outerjoin(target=registrations_for_courses_table).
            group_by(courses_table.c.id).
            cte('course_total_registrations')
        )

        get_courses_stmt = (
            select(
                Bundle("course", *courses_table.c),
                Bundle("course_total_registrations", course_total_registrations.c.total_registered),
            ).
            add_cte(course_total_registrations).
            select_from(courses_table).
            join(course_total_registrations, onclause=courses_table.c.id == course_total_registrations.c.id)
        )

        if filters.author_name:
            get_courses_stmt = (
                get_courses_stmt.
                join(users_table).
                where(users_table.c.fullname.like(f'%{filters.author_name}%'))
            )

        if filters.title:
            get_courses_stmt = (
                get_courses_stmt.
                where(
                    func.concat(
                        func.lower(courses_table.c.title),
                        func.lower(courses_table.c.description),
                    ).like(f'%{filters.title.lower()}%')
                )
            )

        # exclude published courses for everyone
        if not filters.with_creator_id:
            get_courses_stmt = get_courses_stmt.where(courses_table.c.is_published)
        else:
            get_courses_stmt = get_courses_stmt.where(courses_table.c.creator_id == filters.with_creator_id)

        if filters.with_registered_actor_id:
            get_courses_stmt = (
                get_courses_stmt.
                join(
                    target=registrations_for_courses_table,
                    onclause=registrations_for_courses_table.c.user_id == filters.with_registered_actor_id
                )
            )

        if filters.sort_by == SortBy.DATE:
            get_courses_stmt = get_courses_stmt.order_by(desc(courses_table.c.created_at))

        elif filters.sort_by == SortBy.POPULARITY:
            get_courses_stmt = get_courses_stmt.order_by(desc(course_total_registrations.c.total_registered))

        total_res = await self._session.execute(
            select(func.count()).select_from(get_courses_stmt)
        )

        get_courses_stmt = (
            get_courses_stmt.
            offset(pagination.offset).
            limit(pagination.limit)
        )
        res = await self._session.execute(get_courses_stmt)

        courses = []
        for row in res:
            courses.append(Course(
                **row.course._mapping,  # noqa
                total_registered=row.course_total_registrations.total_registered,
            ))

        total = total_res.scalar_one()
        return courses, total

    async def save(self, course: Course) -> CourseID:
        stmt = (
            insert(courses_table).
            values(
                title=course.title,
                creator_id=course.creator_id,
                is_published=course.is_published,
                description=course.description,
                photo_id=course.photo_id,
                created_at=course.created_at,
                updated_at=course.updated_at,
                registrations_limit=course.registrations_limit,
            )
        )

        if course.id:
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                constraint='courses_pkey',
                set_=dict(
                    title=course.title,
                    is_published=course.is_published,
                    description=course.description,
                    photo_id=course.photo_id,
                    registrations_limit=course.registrations_limit,
                    updated_at=course.updated_at,
                ),
                where=(courses_table.c.id == course.id)
            )

        stmt = stmt.returning(courses_table.c.id)

        res = await self._session.execute(stmt)
        return res.scalar_one()

    async def get_share_rules(self, course_id: CourseID) -> Sequence[CourseShareRule]:
        stmt = select(CourseShareRule).where(course_share_rules_table.c.course_id == course_id)

        res = await self._session.scalars(stmt)
        return res.all()


    async def add_share_rule(self, share_rule: CourseShareRule) -> None:
        raise NotImplementedError

    async def delete_share_rule(self, course_id: CourseID, user_id: UserID) -> None:
        raise NotImplementedError


class RegistrationForCourseMapper(RegistrationForCourseGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read(self, user_id: UserID, course_id: CourseID) -> RegistrationForCourse:
        stmt = select(RegistrationForCourse).where(and_(
            registrations_for_courses_table.c.course_id == course_id,
            registrations_for_courses_table.c.user_id == user_id,
        ))
        res = await self._session.execute(stmt)

        return res.scalar_one_or_none()

    async def exists(self, user_id: UserID, course_id: CourseID) -> bool:
        stmt = select(exists(
            select(RegistrationForCourse).
            where(
                and_(
                    registrations_for_courses_table.c.course_id == course_id,
                    registrations_for_courses_table.c.user_id == user_id,
                )
            )
        ))
        res = await self._session.execute(stmt)
        return res.scalar()

    async def save(self, registration: RegistrationForCourse) -> None:
        pass
