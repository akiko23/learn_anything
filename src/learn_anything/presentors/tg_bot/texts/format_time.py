def format_time(total_tasks: int):
    total_spent_minutes = 20 * total_tasks
    spent_hours, spent_minutes = total_spent_minutes // 60, total_spent_minutes % 60

    spent_hours = f'{spent_hours} ч' if spent_hours else ''
    spent_minutes = f'{spent_minutes} мин' if spent_minutes else ''

    return f'{spent_hours} {spent_minutes}'
