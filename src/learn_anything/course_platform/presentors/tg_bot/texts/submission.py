from learn_anything.course_platform.presentors.tg_bot.templates import pre_tm


def get_on_failed_code_submission_text(failed_test_output: str, failed_test_idx: int, attempts_left: int | None) -> str:
    additional_postfix = '...' if len(failed_test_output) > 900 else ''
    output = pre_tm.render(content=failed_test_output[:900] + additional_postfix)

    attempts_left_text = ''
    if attempts_left is not None:
        if attempts_left == 0:
            return (
                'Решение не прошло проверку\n'
                f'Тест #{failed_test_idx + 1} провалился:\n'
                f'\nПопыток не осталось :(\n\n'
                f'{output}'
            )
        attempts_left_text = f'\nОсталось попыток: {attempts_left}\n\n'

    if failed_test_idx == -1:
        return (
            'Решение не прошло проверку, попробуйте еще раз\n'
            f'{attempts_left_text}'
            f'{output}'
        )
    return (
        'Решение не прошло проверку, попробуйте еще раз\n\n'
        f'Тест #{failed_test_idx + 1} провалился:\n'
        f'{attempts_left_text}'
        f'{output}'
    )
