from learn_anything.presentors.tg_bot.templates import pre_tm


def get_on_failed_code_submission_text(output_data, attempts_left: int | None):
    additional_postfix = '...' if len(output_data.failed_output) > 900 else ''
    output = pre_tm.render(content=output_data.failed_output[:900]) + additional_postfix

    attempts_left_text = ''
    if attempts_left is not None:
        if attempts_left == 0:
            return (
                'Решение не прошло проверку\n\n'
                f'Тест #{output_data.failed_test_idx + 1} провалился:\n'
                f'\nПопыток не осталось :(\n\n'
                f'{output}'
            )
        attempts_left_text = f'\nОсталось попыток: {attempts_left}'

    if output_data.failed_test_idx == -1:
        return (
            'Решение не прошло проверку, попробуйте еще раз\n'
            f'{attempts_left_text}\n\n'
            f'{output}'
        )
    return (
        'Решение не прошло проверку, попробуйте еще раз\n\n'
        f'Тест #{output_data.failed_test_idx + 1} провалился:\n'
        f'{attempts_left_text}\n\n'
        f'{output}'
    )
