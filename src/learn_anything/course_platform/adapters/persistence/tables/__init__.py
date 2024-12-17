from .base import metadata as metadata
from .user import (
    users_table as users_table,
    auth_links_table as auth_links_table
)
from .course import (
    courses_table as courses_table,
    registrations_for_courses_table as registrations_for_courses_table
)
from .task import (
    tasks_table as tasks_table,
    code_task_tests_table as code_task_tests_table,
    poll_task_options_table as poll_task_options_table,
    text_input_task_correct_answers_table as text_input_task_correct_answers_table
)
from .submission import submissions_table as submissions_table
