import sqlalchemy as sa

from learn_anything.entities.submission.models import Submission, PollSubmission, CodeSubmission
from learn_anything.adapters.persistence.tables.base import mapper_registry

submissions_table = sa.Table(
    "submissions",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.BigInteger,
        primary_key=True,
        unique=True,
    ),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete='CASCADE')
    ),
    sa.Column(
        "task_id",
        sa.BigInteger,
        sa.ForeignKey("tasks.id", ondelete='CASCADE')
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
    ),
)


def map_submissions_table():
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
