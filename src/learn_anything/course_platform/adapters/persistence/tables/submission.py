import sqlalchemy as sa

from learn_anything.course_platform.domain.entities.submission.models import Submission, PollSubmission, CodeSubmission
from learn_anything.course_platform.adapters.persistence.tables.base import mapper_registry

submissions_table = sa.Table(
    "submissions",
    mapper_registry.metadata,
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete='CASCADE'),
        primary_key=True
    ),
    sa.Column(
        "task_id",
        sa.BigInteger,
        sa.ForeignKey("tasks.id", ondelete='CASCADE'),
        primary_key=True,
    ),
    sa.Column(
        'code',
        sa.Text,
        nullable=True,
    ),
    sa.Column(
        "selected_option_id",
        sa.BigInteger,
        sa.ForeignKey("poll_task_options.id", ondelete='SET NULL'),
        nullable=True,
    ),
    sa.Column('is_correct', sa.Boolean),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
        primary_key=True
    ),
)


def map_submissions_table() -> None:
    mapper_registry.map_imperatively(
        Submission,
        submissions_table
    )
    mapper_registry.map_imperatively(
        CodeSubmission,
        submissions_table
    )
    mapper_registry.map_imperatively(
        PollSubmission,
        submissions_table
    )
