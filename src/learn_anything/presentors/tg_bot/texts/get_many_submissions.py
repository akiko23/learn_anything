from learn_anything.application.interactors.submission.get_many_submissions import SubmissionData


def get_actor_submissions_text(submission_data: SubmissionData, pointer):
    verdict = '✅Верно' if submission_data.is_correct else '❌Неверно'

    return f"""Решение №{pointer + 1}:

```
{submission_data.solution}
```

Вердикт: {verdict}
"""
