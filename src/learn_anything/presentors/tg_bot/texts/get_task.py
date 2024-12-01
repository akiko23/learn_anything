from learn_anything.application.interactors.task.get_course_tasks import TaskData
from learn_anything.entities.task.enums import TaskType
from learn_anything.presentors.tg_bot.texts.formatters import format_date


def get_task_text(task_data: TaskData):
    task_topic = 'Без темы'
    if task_data.topic:
        task_topic = f'Тема: {task_data.topic}'


    creation_date_text = format_date(task_data.created_at)
    last_update_date_text = format_date(task_data.updated_at)
    match task_data.type:
        case TaskType.THEORY:
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

        case TaskType.CODE:
            solved_text = ''
            if task_data.solved_by_actor:
                solved_text = '✅Решено\n\n'

            attempts_left_text = ''
            if task_data.attempts_left:
                attempts_left_text = f'Осталось попыток: {attempts_left_text}\n\n'

            correct_submissions_percentage = (
                round(task_data.total_correct_submissions / max(task_data.total_submissions * 100, 1))
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
                f'{solved_text}'
                f'{attempts_left_text}'
                f'Всего решений отправлено: {task_data.total_submissions}\n'
                f'Из них верных: {correct_submissions_percentage}%\n'
                f'\n'
                f'Создано: {creation_date_text}\n'
                f'Обновлено: {last_update_date_text}\n'
            )
        case _:
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
