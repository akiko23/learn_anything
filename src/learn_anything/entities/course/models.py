from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from learn_anything.entities.user.models import UserID

CourseID = NewType("CourseID", int)


@dataclass
class Course:
    id: CourseID | None
    title: str
    description: str
    photo_path: str | None
    creator_id: UserID
    is_published: bool


@dataclass
class RegistrationForCourse:
    user_id: UserID
    course_id: CourseID
    created_at: datetime
