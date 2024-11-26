class UserNotAuthenticatedError(Exception):
    message: str = "User not authenticated"


class TokenDecodeError(Exception):
    message: str = "Token is invalid"

