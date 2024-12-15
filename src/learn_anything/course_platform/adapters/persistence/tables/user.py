import datetime
import uuid

import sqlalchemy as sa
# from sqlalchemy.orm import relationship

from learn_anything.course_platform.domain.entities.user.models import User, UserRole, AuthLink
from learn_anything.course_platform.adapters.persistence.tables.base import mapper_registry

users_table = sa.Table(
    "users",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.BigInteger,
        primary_key=True,
        unique=True,
    ),
    sa.Column("fullname", sa.String(256), nullable=False),
    sa.Column(
        "username",
        sa.String(256),
        nullable=True,
        default=None,
    ),
    sa.Column("role", sa.Enum(UserRole), nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
)

auth_links_table = sa.Table(
    "auth_links",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.Uuid,
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        server_default=sa.text("uuid_generate_v4()"),
    ),
    sa.Column(
        "expires_at",
        sa.DateTime,
        default=lambda: datetime.datetime.now() + datetime.timedelta(days=5),
    ),
    sa.Column(
        "usages",
        sa.Integer,
        default=1,
    ),
    sa.Column(
        "for_role",
        sa.Enum(UserRole)
    ),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        # properties={
        #     "shops": relationship(
        #         "Shop",
        #         secondary=association_between_shops_and_users,
        #         back_populates="users",
        #     ),
        # },
    )
    mapper_registry.map_imperatively(
        AuthLink,
        auth_links_table,
    )
