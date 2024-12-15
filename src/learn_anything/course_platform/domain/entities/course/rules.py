from collections.abc import Sequence
from datetime import datetime

from learn_anything.course_platform.domain.entities.course.errors import RegistrationsLimitExceededError, CoursePermissionError
from learn_anything.course_platform.domain.entities.course.models import Course, CourseID, RegistrationForCourse, CourseShareRule
from learn_anything.course_platform.domain.entities.user.models import UserID


def create_course(
        id_: CourseID | None,
        title: str,
        creator_id: UserID,
        description: str,
        is_published: bool,
        photo_id: str | None,
        registrations_limit: str | None,
) -> Course:
    return Course(
        id=id_,
        title=title,
        description=description,
        photo_id=photo_id,
        creator_id=creator_id,
        is_published=is_published,
        registrations_limit=registrations_limit,
        total_registered=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def increment_course_registrations_number(course: Course) -> Course:
    if not course.registrations_limit:
        course.total_registered += 1
        return course

    if course.registrations_limit > course.total_registered + 1:
        raise RegistrationsLimitExceededError(course.id)

    course.total_registered += 1
    return course


def decrement_course_registrations_number(course: Course) -> Course:
    course.total_registered -= 1
    return course


def create_registration_for_course(user_id: UserID, course_id: CourseID):
    return RegistrationForCourse(
        user_id=user_id,
        course_id=course_id,
        created_at=datetime.now(),
    )


def ensure_actor_has_read_access(actor_id: UserID, course: Course, share_rules: Sequence[CourseShareRule]):
    if course.is_published:
        return

    if actor_id == course.creator_id:
        return

    for share_rule in share_rules:
        if actor_id == share_rule.user_id:
            return

    raise CoursePermissionError


def ensure_actor_has_write_access(actor_id: UserID, course: Course, share_rules: Sequence[CourseShareRule]):
    if actor_id == course.creator_id:
        return

    for share_rule in share_rules:
        if actor_id == share_rule.user_id and share_rule.write_allowed:
            return

    raise CoursePermissionError


def actor_has_write_access(actor_id: UserID, course: Course, share_rules: Sequence[CourseShareRule]):
    try:
        ensure_actor_has_write_access(actor_id=actor_id, course=course, share_rules=share_rules)
    except CoursePermissionError:
        return False
    return True
