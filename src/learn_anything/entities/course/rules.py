from datetime import datetime
from typing import Optional

from learn_anything.entities.course.models import Course, CourseID, RegistrationForCourse
from learn_anything.entities.user.models import UserID


def create_course(
        id_: CourseID | None,
        title: str,
        creator_id: UserID,
        description: str,
        is_published: bool,
        photo_path: str | None,
) -> Course:
    return Course(
        id=id_,
        title=title,
        description=description,
        photo_path=photo_path,
        creator_id=creator_id,
        is_published=is_published,
    )


def create_registration_for_course(user_id: UserID, course_id: CourseID) -> RegistrationForCourse:
    return RegistrationForCourse(
        user_id=user_id,
        course_id=course_id,
        created_at=datetime.now(),
    )
