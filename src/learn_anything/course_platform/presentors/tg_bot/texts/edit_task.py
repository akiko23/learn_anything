def get_edit_code_task_attempts_limit_text(current_attempts_limit: int | None) -> str:
    if current_attempts_limit is not None:
        return f'Отправьте новый лимит на количество попыток (не меньше чем {current_attempts_limit})'
    return 'Отправьте новый лимит на количество попыток'

