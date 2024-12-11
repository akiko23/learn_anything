from collections.abc import Iterable
from datetime import datetime
from typing import Sequence

from learn_anything.domain.entities.course.models import CourseID
from learn_anything.domain.entities.submission.models import Submission
from learn_anything.domain.entities.task.enums import TaskType
from learn_anything.domain.entities.task.models import PollTask, PollTaskOptionID, TextInputTask, TextInputTaskAnswer, \
    CodeTask, CodeTaskTest


def find_task_option_by_id(task: PollTask, target_option_id: PollTaskOptionID):
    for option in task.options:
        if option.id == target_option_id:
            return option


def answer_is_correct(task: TextInputTask, answer: TextInputTaskAnswer) -> bool:
    if answer in task.correct_answers:
        return True
    return False


def create_code_task(
        title: str,
        body: str,
        topic: str | None,
        course_id: CourseID,
        index_in_course: int,
        prepared_code: str | None,
        code_duration_timeout: int,
        tests: Sequence[str],
        attempts_limit: int,
):
    return CodeTask(
        id=None,
        title=title,
        type=TaskType.CODE,
        body=body,
        topic=topic,
        course_id=course_id,
        index_in_course=index_in_course,
        prepared_code=prepared_code,
        code_duration_timeout=code_duration_timeout,
        tests=[CodeTaskTest(code=code) for i, code in enumerate(tests)],
        attempts_limit=attempts_limit,
        created_at=datetime.now()
    )


def is_task_solved_by_actor(actor_submissions: Iterable[Submission]) -> bool:
    for submission in actor_submissions:
        if submission.is_correct:
            return True
    return False


def code_task_test_exists(code_task: CodeTask, test_code: str):
    for code_task_test in code_task.tests:
        if code_task_test.code == test_code:
            return True
    return False


def update_code_task_test(task: CodeTask, index_in_task: int, new_code: str | None):
    if new_code is None:
        task.tests[index_in_task].code = None
        return task

    task.tests[index_in_task].code = new_code
    return task
