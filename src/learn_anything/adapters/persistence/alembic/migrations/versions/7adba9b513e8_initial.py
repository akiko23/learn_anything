"""initial

Revision ID: b639b08e3589
Revises:
Create Date: 2024-11-22 11:23:22.487568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b639b08e3589'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_links',
    sa.Column('id', sa.Uuid(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('usages', sa.Integer(), nullable=True),
    sa.Column('for_role', sa.Enum('STUDENT', 'MENTOR', 'MODERATOR', 'BOT_OWNER', name='userrole'), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('fullname', sa.String(length=256), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=True),
    sa.Column('role', sa.Enum('STUDENT', 'MENTOR', 'MODERATOR', 'BOT_OWNER', name='userrole'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('courses',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('photo_id', sa.String(length=512), nullable=True),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('registrations_limit', sa.BigInteger(), nullable=True),
    sa.Column('creator_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('course_share_rules',
    sa.Column('course_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('can_write', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('course_id', 'user_id')
    )
    op.create_table('registrations_for_courses',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('course_id', sa.BigInteger(), nullable=False),
    sa.Column('registered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id', 'registered_at')
    )
    op.create_table('tasks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('topic', sa.String(length=256), nullable=True),
    sa.Column('type', sa.Enum('THEORY', 'CODE', 'POLL', 'TEXT_INPUT', name='tasktype'), nullable=True),
    sa.Column('course_id', sa.BigInteger(), nullable=True),
    sa.Column('index_in_course', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('prepared_code', sa.Text(), nullable=True),
    sa.Column('code_duration_timeout', sa.BigInteger(), nullable=True),
    sa.Column('attempts_limit', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('code_task_tests',
    sa.Column('index_in_task', sa.BigInteger(), nullable=False),
    sa.Column('code', sa.Text(), nullable=False),
    sa.Column('task_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('code', 'task_id'),
    )
    op.create_table('poll_task_options',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('task_id', sa.BigInteger(), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('text_input_task_correct_answers',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('value', sa.Text(), nullable=True),
    sa.Column('task_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('submissions',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('task_id', sa.BigInteger(), nullable=False),
    sa.Column('code', sa.Text(), nullable=True),
    sa.Column('selected_option_id', sa.BigInteger(), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['selected_option_id'], ['poll_task_options.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'task_id', 'created_at')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('submissions')
    op.drop_table('text_input_task_correct_answers')
    op.drop_table('poll_task_options')
    op.drop_table('code_task_tests')
    op.drop_table('tasks')
    op.drop_table('registrations_for_courses')
    op.drop_table('course_share_rules')
    op.drop_table('courses')
    op.drop_table('users')
    op.drop_table('auth_links')
    # ### end Alembic commands ###