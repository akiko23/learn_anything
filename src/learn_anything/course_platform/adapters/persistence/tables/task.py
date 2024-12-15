import sqlalchemy as sa

from learn_anything.course_platform.adapters.persistence.tables.base import mapper_registry
from learn_anything.course_platform.domain.entities.task.enums import TaskType
from learn_anything.course_platform.domain.entities.task.models import Task, CodeTask, PollTask, PollTaskOption, TextInputTask, \
    TextInputTaskAnswer, CodeTaskTest

tasks_table = sa.Table(
    "tasks",
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
        "body",
        sa.Text,
    ),
    sa.Column(
        "topic",
        sa.String(256),
        nullable=True,
    ),
    sa.Column(
        'type',
        sa.Enum(TaskType),
    ),
    sa.Column(
        "course_id",
        sa.BigInteger,
        sa.ForeignKey("courses.id", ondelete='CASCADE')
    ),
    sa.Column(
        "index_in_course",
        sa.Integer,
    ),
    sa.Column(
        "created_at",
        sa.DateTime,
        default=sa.func.now(),
        server_default=sa.func.now(),
    ),
    sa.Column(
        "prepared_code",
        sa.Text,
        nullable=True,
    ),
    sa.Column(
        "code_duration_timeout",
        sa.BigInteger,
        nullable=True
    ),
    sa.Column(
        "attempts_limit",
        sa.BigInteger,
        nullable=True,
    )
)

code_task_tests_table = sa.Table(
    "code_task_tests",
    mapper_registry.metadata,
    sa.Column(
        "index_in_task",
        sa.BigInteger,
        nullable=False,
    ),
    sa.Column(
        "code",
        sa.Text,
        nullable=False,
        primary_key=True
    ),
    sa.Column(
        "task_id",
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True
    ),
)

poll_task_options_table = sa.Table(
    "poll_task_options",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
    ),
    sa.Column(
        "content",
        sa.Text,
    ),
    sa.Column(
        "task_id",
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "is_correct",
        sa.Boolean,
    )
)

text_input_task_correct_answers_table = sa.Table(
    "text_input_task_correct_answers",
    mapper_registry.metadata,
    sa.Column(
        "id",
        sa.BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
    ),
    sa.Column(
        "value",
        sa.Text,
    ),
    sa.Column(
        "task_id",
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
    ),
)


def map_tasks_table() -> None:
    mapper_registry.map_imperatively(
        Task,
        tasks_table,
    )

    mapper_registry.map_imperatively(
        CodeTask,
        tasks_table,
    )
    mapper_registry.map_imperatively(
        CodeTaskTest,
        code_task_tests_table,
    )

    mapper_registry.map_imperatively(
        PollTask,
        tasks_table,
    )
    mapper_registry.map_imperatively(
        PollTaskOption,
        poll_task_options_table,
    )

    mapper_registry.map_imperatively(
        TextInputTask,
        tasks_table,
    )
    mapper_registry.map_imperatively(
        TextInputTaskAnswer,
        text_input_task_correct_answers_table,
    )
