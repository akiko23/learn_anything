from learn_anything.entities.user.models import User, UserID, UserRole


def create_user(user_id: int, fullname: str, username: str, role: UserRole) -> User:
    return User(id=UserID(user_id), fullname=fullname, username=username, role=role)
