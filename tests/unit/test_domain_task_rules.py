from datetime import datetime

import pytest

from learn_anything.course_platform.domain.entities.course.models import CourseID
from learn_anything.course_platform.domain.entities.submission.models import Submission
from learn_anything.course_platform.domain.entities.task.enums import TaskType
from learn_anything.course_platform.domain.entities.task.errors import (
    CanNotSetAttemptsLimitError,
)
from learn_anything.course_platform.domain.entities.task.models import (
    CodeTask,
    CodeTaskTest,
    PollTask,
    PollTaskOption,
    PollTaskOptionID,
    Task,
    TaskID,
    TextInputTask,
    TextInputTaskAnswer,
)
from learn_anything.course_platform.domain.entities.task.rules import (
    answer_is_correct,
    create_code_task,
    create_poll_task,
    create_theory_task,
    find_task_option_by_id,
    is_task_solved_by_actor,
    update_code_task_attempts_limit,
)
from learn_anything.course_platform.domain.entities.user.models import UserID


def test_create_theory_task():
    t = create_theory_task(
        id_=TaskID(1),
        title="T",
        body="B",
        topic="X",
        course_id=CourseID(1),
        index_in_course=0,
    )
    assert t.id == 1
    assert t.type == TaskType.THEORY
    assert t.title == "T"
    assert t.course_id == 1


def test_create_code_task():
    t = create_code_task(
        id_=TaskID(2),
        title="Code",
        body="B",
        topic=None,
        course_id=CourseID(1),
        index_in_course=1,
        prepared_code="x=1",
        code_duration_timeout=10,
        tests=["assert 1==1"],
        attempts_limit=3,
    )
    assert t.type == TaskType.CODE
    assert len(t.tests) == 1
    assert t.tests[0].code == "assert 1==1"
    assert t.attempts_limit == 3


def test_create_poll_task():
    opt = PollTaskOption(id=PollTaskOptionID(1), content="A", is_correct=True)
    t = create_poll_task(
        id_=TaskID(3),
        title="Poll",
        body="B",
        topic=None,
        course_id=CourseID(1),
        index_in_course=0,
        options=[opt],
        attempts_limit=None,
    )
    assert t.type == TaskType.POLL
    assert len(t.options) == 1
    assert t.options[0].is_correct is True


def test_is_task_solved_by_actor_true():
    subs = [
        Submission(user_id=UserID(1), task_id=TaskID(1), is_correct=False, created_at=datetime.now()),
        Submission(user_id=UserID(1), task_id=TaskID(1), is_correct=True, created_at=datetime.now()),
    ]
    assert is_task_solved_by_actor(subs) is True


def test_is_task_solved_by_actor_false():
    subs = [
        Submission(user_id=UserID(1), task_id=TaskID(1), is_correct=False, created_at=datetime.now()),
    ]
    assert is_task_solved_by_actor(subs) is False


def test_is_task_solved_by_actor_empty():
    assert is_task_solved_by_actor([]) is False


def test_find_task_option_by_id():
    opt1 = PollTaskOption(id=PollTaskOptionID(1), content="A", is_correct=False)
    opt2 = PollTaskOption(id=PollTaskOptionID(2), content="B", is_correct=True)
    t = create_poll_task(
        id_=TaskID(1),
        title="P",
        body="",
        topic=None,
        course_id=CourseID(1),
        index_in_course=0,
        options=[opt1, opt2],
        attempts_limit=None,
    )
    found = find_task_option_by_id(t, PollTaskOptionID(2))
    assert found is not None
    assert found.content == "B" and found.is_correct is True


def test_find_task_option_by_id_not_found():
    opt = PollTaskOption(id=PollTaskOptionID(1), content="A", is_correct=True)
    t = create_poll_task(
        id_=TaskID(1),
        title="P",
        body="",
        topic=None,
        course_id=CourseID(1),
        index_in_course=0,
        options=[opt],
        attempts_limit=None,
    )
    assert find_task_option_by_id(t, PollTaskOptionID(999)) is None


def test_answer_is_correct():
    a1 = TextInputTaskAnswer(value="yes")
    a2 = TextInputTaskAnswer(value="no")
    t = TextInputTask(
        id=TaskID(1),
        type=TaskType.TEXT_INPUT,
        title="",
        body="",
        topic=None,
        course_id=CourseID(1),
        index_in_course=0,
        correct_answers=[a1, a2],
        attempts_limit=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert answer_is_correct(t, TextInputTaskAnswer(value="yes")) is True
    assert answer_is_correct(t, TextInputTaskAnswer(value="no")) is True
    assert answer_is_correct(t, TextInputTaskAnswer(value="other")) is False


def test_update_code_task_attempts_limit_set_none():
    t = create_code_task(
        id_=TaskID(1),
        title="",
        body="",
        topic=None,
        course_id=CourseID(1),
        index_in_course=0,
        prepared_code=None,
        code_duration_timeout=5,
        tests=[],
        attempts_limit=3,
    )
    out = update_code_task_attempts_limit(t, None)
    assert out.attempts_limit is None


def test_update_code_task_attempts_limit_increase_raises():
    t = create_code_task(
        id_=TaskID(1),
        title="",
        body="",
        topic=None,
        course_id=CourseID(1),
        index_in_course=0,
        prepared_code=None,
        code_duration_timeout=5,
        tests=[],
        attempts_limit=3,
    )
    with pytest.raises(CanNotSetAttemptsLimitError):
        update_code_task_attempts_limit(t, 5)
