from datetime import datetime
from typing import Sequence

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.models import PollTask, PollTaskOptionID, TextInputTask, TextInputTaskAnswer, \
    TaskType, CodeTask, CodeTaskTest


def option_is_correct(task: PollTask, option_id: PollTaskOptionID):
    for option in task.options:
        if option.is_correct and option.id == option_id:
            return True
    return False


def answer_is_correct(task: TextInputTask, answer: TextInputTaskAnswer) -> bool:
    if answer in task.correct_answers:
        return True
    return False



def create_code_task(
        title: str,
        body: str,
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
        course_id=course_id,
        index_in_course=index_in_course,
        prepared_code=prepared_code,
        code_duration_timeout=code_duration_timeout,
        tests=[CodeTaskTest(code=code) for code in tests],
        attempts_limit=attempts_limit,
        created_at=datetime.now()
    )
