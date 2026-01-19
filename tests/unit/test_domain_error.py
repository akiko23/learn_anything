from learn_anything.course_platform.domain.entities.course.errors import (
    CourseDoesNotExistError,
    CoursePermissionError,
)
from learn_anything.course_platform.domain.error import ApplicationError


def test_course_does_not_exist_error_message():
    err = CourseDoesNotExistError(course_id=42)
    assert err.message == 'Course with provided id="42" does not exist'


def test_course_permission_error_message():
    err = CoursePermissionError()
    assert "don't have read or write access" in err.message


def test_application_error_subclass():
    assert issubclass(CourseDoesNotExistError, ApplicationError)
