import uuid
from datetime import datetime

from learn_anything.course_platform.domain.entities.user.enums import UserRole
from learn_anything.course_platform.domain.entities.user.models import User, UserID, AuthLink
from learn_anything.course_platform.domain.value_objects.expires_at import ExpiresAt


def create_user(id_: UserID, fullname: str, username: str | None, role: UserRole) -> User:
    return User(id=id_, fullname=fullname, username=username, role=role)


def create_auth_link(link_id: uuid.UUID | None, for_role: UserRole, usages: int, expires_at: datetime) -> AuthLink:
    return AuthLink(
        id=link_id,
        for_role=for_role,
        usages=usages,
        expires_at=ExpiresAt(expires_at).value,
    )
