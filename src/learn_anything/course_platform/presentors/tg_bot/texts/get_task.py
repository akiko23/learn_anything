from jinja2 import Template

from learn_anything.course_platform.application.interactors.task.get_course_tasks import TheoryTaskData, \
    CodeTaskData
from learn_anything.course_platform.presentors.tg_bot.texts.formatters import format_date

prepared_code_tm = Template(
    (
        'Предварительный код:\n'
        '<pre><code class="language-python">'
        '{{ prepared_code }}'
        '</code></pre>\n\n\n'
    )
)


def get_task_text(task_data: TheoryTaskData | CodeTaskData) -> str:
    task_topic = 'Без темы'
    if task_data.topic:
        task_topic = f'Тема: {task_data.topic}'

    creation_date_text = format_date(task_data.created_at)
    last_update_date_text = format_date(task_data.updated_at)
    if isinstance(task_data, TheoryTaskData):
        text = (
            f'{task_data.title}\n'
            f'\n'
            f'Тип: Теоретическое задание\n'
            f'\n'
            f'{task_topic}\n'
            f'\n'
            f'Тело: {task_data.body}\n'
            f'\n'
            f'Создано: {creation_date_text}\n'
            f'Обновлено: {last_update_date_text}\n'
        )

    elif isinstance(task_data, CodeTaskData):
        solved_text = ''
        if task_data.solved_by_actor:
            solved_text = '✅Решено\n\n'

        attempts_left_text = ''
        if task_data.attempts_limit is not None:
            attempts_left = max(task_data.attempts_limit - task_data.total_actor_submissions, 0)
            attempts_left_text = f'Осталось попыток: {attempts_left}\n\n'

        prepared_code_text = ''
        if task_data.actor_has_write_access and task_data.prepared_code is not None:
            prepared_code_text = prepared_code_tm.render(prepared_code=task_data.prepared_code)

        correct_submissions_percentage = (
            round(task_data.total_correct_submissions / max(task_data.total_submissions, 1) * 100)
        )
        text = (
            f'{task_data.title}\n'
            f'\n'
            f'Тип: Задание на код\n'
            f'\n'
            f'{task_topic}\n'
            f'\n'
            f'Тело: {task_data.body}\n'
            f'\n'
            f'Макс. время выполнения: {task_data.code_duration_timeout} с.\n'
            f'\n'
            f'{prepared_code_text}'
            f'{solved_text}'
            f'{attempts_left_text}'
            f'Всего решений отправлено: {task_data.total_submissions}\n'
            f'Из них верных: {correct_submissions_percentage}%\n'
            f'\n'
            f'Создано: {creation_date_text}\n'
            f'Обновлено: {last_update_date_text}\n'
        )
    else:
        text = (
            f'{task_data.title}\n'
            f'\n'
            f'Тип: {task_data.type}\n'
            f'\n'
            f'{task_topic}\n'
            f'\n'
            f'Тело: {task_data.body}\n'
            f'\n'
            f'Создано: {task_data.created_at}\n'
        )

    return text


def get_task_text_on_edit(task_data: TheoryTaskData | CodeTaskData) -> str:
    text = get_task_text(task_data=task_data)
    text += '\n\nВыберите, что хотите изменить.'
    if not task_data.is_published and isinstance(task_data, CodeTaskData):
        text += '\nУчтите, лимит на количество попыток можно выставлять лишь до публикации задания'
    return text