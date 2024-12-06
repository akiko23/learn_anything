def get_on_failed_code_submission_text(output_data, attempts_left: int | None):
    attempts_left_text = ''
    if attempts_left is not None:
        if attempts_left == 0:
            return (
                'Решение не прошло проверку\n\n'
                f'Тест #{output_data.failed_test_idx + 1} провалился:\n'
                f'```\n{output_data.failed_output[:500]}```\n'
                f'\nПопыток не осталось :('
            )
        attempts_left_text = f'\nОсталось попыток: {attempts_left}'

    if output_data.failed_test_idx == -1:
        return (
            'Решение не прошло проверку, попробуйте еще раз\n\n'
            f'```\n{output_data.failed_output[:500] + '...'}```\n'
            f'{attempts_left_text}'
        )
    return (
        'Решение не прошло проверку, попробуйте еще раз\n\n'
        f'Тест #{output_data.failed_test_idx + 1} провалился:\n'
        f'```\n{output_data.failed_output[:500]}```\n'
        f'{attempts_left_text}'
    )
