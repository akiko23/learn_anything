from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from learn_anything.course_platform.domain.entities.user.models import UserID

CourseID = NewType("CourseID", int)


@dataclass
class Course:
    id: CourseID | None
    title: str
    description: str
    photo_id: str | None
    creator_id: UserID
    is_published: bool
    created_at: datetime
    updated_at: datetime
    registrations_limit: int | None
    total_registered: int


@dataclass
class RegistrationForCourse:
    user_id: UserID
    course_id: CourseID
    created_at: datetime


# Soon...
@dataclass
class CourseShareRule:
    course_id: CourseID
    user_id: UserID
    write_allowed: bool
