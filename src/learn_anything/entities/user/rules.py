import uuid
from datetime import datetime
from typing import Optional

from learn_anything.entities.user.models import User, UserID, UserRole, AuthLink
from learn_anything.entities.user.value_objects import AvailableForAuthRole, ExpiresAt


def create_user(user_id: int, fullname: str, username: str | None, role: UserRole) -> User:
    return User(id=UserID(user_id), fullname=fullname, username=username, role=role)


def create_auth_link(link_id: uuid.UUID | None, for_role: UserRole, usages: int, expires_at: str):
    return AuthLink(
        id=link_id,
        for_role=AvailableForAuthRole(for_role).value,
        usages=usages,
        expires_at=ExpiresAt(expires_at).value,
    )
