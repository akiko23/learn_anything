from datetime import datetime


def format_time(total_tasks: int) -> str:
    total_spent_minutes = 20 * total_tasks
    spent_hours, spent_minutes = total_spent_minutes // 60, total_spent_minutes % 60

    spent_hours_str = f'{spent_hours} ч' if spent_hours else ''
    spent_minutes_str = f'{spent_minutes} мин' if spent_minutes else ''

    if not (spent_hours_str and spent_minutes_str):
        return '0'
    return f'{spent_hours_str} {spent_minutes_str}'



def format_date(date: datetime) -> str:
    return date.strftime('%d.%m.%Y %H:%M')
