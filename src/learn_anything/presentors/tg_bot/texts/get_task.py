from learn_anything.application.interactors.task.get_course_tasks import AnyTaskData
from learn_anything.entities.task.models import TaskType


def get_task_text(task_data: AnyTaskData):
    task_topic = 'Без темы'
    if task_data.topic:
        task_topic = f'Тема: {task_data.topic}'

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
                f'Создано: {task_data.created_at}\n'
            )

        case TaskType.CODE:
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
                f'Решений отправлено: {task_data.total_submissions}\n'
                f'\n'
                f'Создано: {task_data.created_at}\n'
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
