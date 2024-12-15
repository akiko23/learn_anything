import sqlalchemy as sa

from learn_anything.course_platform.domain.entities.course.models import Course, RegistrationForCourse, CourseShareRule
from learn_anything.course_platform.adapters.persistence.tables.base import mapper_registry

courses_table = sa.Table(
    "courses",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
    ),
    sa.Column("title", sa.String(256), nullable=False),
    sa.Column(
        "description",
        sa.Text,
    ),
    sa.Column(
        'photo_id',
        sa.String(512)
    ),
    sa.Column(
        "is_published",
        sa.Boolean,
    ),
    sa.Column(
        "registrations_limit",
        sa.BigInteger,
        nullable=True,
    ),
    sa.Column(
        "creator_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete='SET NULL'),
        nullable=True,
    ),
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

course_share_rules_table = sa.Table(
    'course_share_rules',
    mapper_registry.metadata,
    sa.Column(
        "course_id",
        sa.BigInteger,
        sa.ForeignKey("courses.id", ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        'can_write',
        sa.Boolean
    )
)

registrations_for_courses_table = sa.Table(
    "registrations_for_courses",
    mapper_registry.metadata,
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        "course_id",
        sa.BigInteger,
        sa.ForeignKey("courses.id", ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        "registered_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        primary_key=True,
    ),
)


def map_courses_table() -> None:
    mapper_registry.map_imperatively(
        Course,
        courses_table,
    )
    mapper_registry.map_imperatively(
        CourseShareRule,
        course_share_rules_table
    )
    mapper_registry.map_imperatively(
        RegistrationForCourse,
        registrations_for_courses_table,
    )
