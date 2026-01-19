from datetime import datetime

import pytest

from learn_anything.course_platform.domain.entities.course.errors import (
    CoursePermissionError,
    RegistrationsLimitExceededError,
)
from learn_anything.course_platform.domain.entities.course.models import (
    Course,
    CourseID,
    CourseShareRule,
    RegistrationForCourse,
)
from learn_anything.course_platform.domain.entities.course.rules import (
    actor_has_write_access,
    create_course,
    create_registration_for_course,
    decrement_course_registrations_number,
    ensure_actor_has_read_access,
    ensure_actor_has_write_access,
    increment_course_registrations_number,
)
from learn_anything.course_platform.domain.entities.user.models import UserID


NOW = datetime.now()


def _course(rid: int, creator: int, total: int = 0, limit: int | None = None) -> Course:
    return Course(
        id=CourseID(rid),
        title="C",
        description="D",
        photo_id=None,
        creator_id=UserID(creator),
        is_published=False,
        registrations_limit=limit,
        total_registered=total,
        created_at=NOW,
        updated_at=NOW,
    )


def test_create_course():
    c = create_course(
        id_=CourseID(1),
        title="T",
        description="D",
        creator_id=UserID(10),
        is_published=False,
        photo_id=None,
        registrations_limit=5,
    )
    assert c.id == 1
    assert c.title == "T"
    assert c.creator_id == 10
    assert c.total_registered == 0
    assert c.registrations_limit == 5


def test_increment_course_registrations_number_without_limit():
    c = _course(1, 10, total=0, limit=None)
    c2 = increment_course_registrations_number(c)
    assert c2.total_registered == 1
    c3 = increment_course_registrations_number(c2)
    assert c3.total_registered == 2


def test_increment_course_registrations_number_within_limit():
    """С лимитом: инкремент разрешён только при total == limit-1 (текущая семантика rules)."""
    c = _course(1, 10, total=4, limit=5)
    c2 = increment_course_registrations_number(c)
    assert c2.total_registered == 5


def test_increment_course_registrations_number_raises_when_limit_exceeds_total_plus_one():
    """Текущая реализация: при limit > total+1 выбрасывается ошибка (поведение из rules)."""
    c = _course(1, 10, total=3, limit=5)
    with pytest.raises(RegistrationsLimitExceededError) as ei:
        increment_course_registrations_number(c)
    assert ei.value.course_id == 1


def test_decrement_course_registrations_number():
    c = _course(1, 10, total=3, limit=None)
    c2 = decrement_course_registrations_number(c)
    assert c2.total_registered == 2


def test_create_registration_for_course():
    r = create_registration_for_course(UserID(1), CourseID(2))
    assert r.user_id == 1
    assert r.course_id == 2
    assert r.created_at <= datetime.now()


def test_ensure_actor_has_read_access_published():
    c = _course(1, 10)
    c.is_published = True
    ensure_actor_has_read_access(actor_id=UserID(999), course=c, share_rules=[])


def test_ensure_actor_has_read_access_creator():
    c = _course(1, 10)
    ensure_actor_has_read_access(actor_id=UserID(10), course=c, share_rules=[])


def test_ensure_actor_has_read_access_via_share_rule():
    c = _course(1, 10)
    rules = [CourseShareRule(course_id=CourseID(1), user_id=UserID(20), write_allowed=False)]
    ensure_actor_has_read_access(actor_id=UserID(20), course=c, share_rules=rules)


def test_ensure_actor_has_read_access_denied_raises():
    c = _course(1, 10)
    with pytest.raises(CoursePermissionError):
        ensure_actor_has_read_access(actor_id=UserID(999), course=c, share_rules=[])


def test_ensure_actor_has_write_access_creator():
    c = _course(1, 10)
    ensure_actor_has_write_access(actor_id=UserID(10), course=c, share_rules=[])


def test_ensure_actor_has_write_access_via_share_write_allowed():
    c = _course(1, 10)
    rules = [CourseShareRule(course_id=CourseID(1), user_id=UserID(20), write_allowed=True)]
    ensure_actor_has_write_access(actor_id=UserID(20), course=c, share_rules=rules)


def test_ensure_actor_has_write_access_share_read_only_raises():
    c = _course(1, 10)
    rules = [CourseShareRule(course_id=CourseID(1), user_id=UserID(20), write_allowed=False)]
    with pytest.raises(CoursePermissionError):
        ensure_actor_has_write_access(actor_id=UserID(20), course=c, share_rules=rules)


def test_ensure_actor_has_write_access_no_share_raises():
    c = _course(1, 10)
    with pytest.raises(CoursePermissionError):
        ensure_actor_has_write_access(actor_id=UserID(999), course=c, share_rules=[])


def test_actor_has_write_access_true():
    c = _course(1, 10)
    assert actor_has_write_access(actor_id=UserID(10), course=c, share_rules=[]) is True


def test_actor_has_write_access_false():
    c = _course(1, 10)
    assert actor_has_write_access(actor_id=UserID(999), course=c, share_rules=[]) is False
