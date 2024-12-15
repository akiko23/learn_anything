from learn_anything.course_platform.adapters.persistence.tables.course import map_courses_table
from learn_anything.course_platform.adapters.persistence.tables.submission import map_submissions_table
from learn_anything.course_platform.adapters.persistence.tables.task import map_tasks_table
from learn_anything.course_platform.adapters.persistence.tables.user import map_users_table


def map_tables():
    map_users_table()
    map_courses_table()
    map_tasks_table()
    map_submissions_table()
