from learn_anything.course_platform.adapters.auth.errors import (
    TokenDecodeError,
    UserAlreadyAuthenticatedError,
    UserDoesNotExistError,
)


def test_token_decode_error():
    err = TokenDecodeError()
    assert "invalid" in err.message


def test_user_already_authenticated_error():
    err = UserAlreadyAuthenticatedError()
    assert "already" in err.message


def test_user_does_not_exist_error():
    err = UserDoesNotExistError()
    assert "credentials" in err.message
