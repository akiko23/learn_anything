import pytest

from learn_anything.course_platform.application.errors import UserNotAuthenticatedError


def test_user_not_authenticated_error():
    err = UserNotAuthenticatedError()
    assert err.message == "User not authenticated"
