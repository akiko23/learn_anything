import uuid
from datetime import datetime

from learn_anything.entities.user.models import User, UserID, UserRole, AuthLink
from learn_anything.entities.value_objects.expires_at import ExpiresAt


def create_user(user_id: int, fullname: str, username: str | None, role: UserRole) -> User:
    return User(id=UserID(user_id), fullname=fullname, username=username, role=role)


def create_auth_link(link_id: uuid.UUID | None, for_role: UserRole, usages: int, expires_at: datetime):
    return AuthLink(
        id=link_id,
        for_role=for_role,
        usages=usages,
        expires_at=ExpiresAt(expires_at).value,
    )
