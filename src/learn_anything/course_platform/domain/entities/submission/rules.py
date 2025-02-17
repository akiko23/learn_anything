from datetime import datetime

from learn_anything.course_platform.domain.entities.submission.models import CodeSubmission
from learn_anything.course_platform.domain.entities.task.models import TaskID
from learn_anything.course_platform.domain.entities.user.models import UserID


def create_code_submission(
        user_id: UserID,
        code: str,
        task_id: TaskID,
        tests_result_output: str,
) -> CodeSubmission:
    is_correct = False
    if tests_result_output == 'ok':
        is_correct = True

    return CodeSubmission(
        user_id=user_id,
        task_id=task_id,
        code=code,
        is_correct=is_correct,
        created_at=datetime.now(),
    )
