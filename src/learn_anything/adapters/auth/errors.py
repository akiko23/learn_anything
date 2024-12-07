class UserNotAuthenticatedError(Exception):
    message: str = "User not authenticated"


class TokenDecodeError(Exception):
    message: str = "Token is invalid"


class UserAlreadyAuthenticatedError(Exception):
    message: str = "User is already authenticated"



class UserDoesNotExistError(Exception):
    message: str = "User with provided credentials does not exist"
