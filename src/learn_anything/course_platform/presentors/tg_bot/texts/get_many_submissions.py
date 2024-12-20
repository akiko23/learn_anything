from learn_anything.course_platform.application.interactors.submission.get_many_submissions import SubmissionData
from learn_anything.course_platform.presentors.tg_bot.texts.formatters import format_date
from learn_anything.course_platform.presentors.tg_bot.templates import python_code_tm


def get_actor_submissions_text(submission_data: SubmissionData, pointer: int) -> str:
    verdict = '✅Верно' if submission_data.is_correct else '❌Неверно'

    return f"""Решение №{pointer + 1}:

{python_code_tm.render(code=submission_data.solution)}

Вердикт: {verdict}

Отправлено: {format_date(submission_data.created_at)}
"""
