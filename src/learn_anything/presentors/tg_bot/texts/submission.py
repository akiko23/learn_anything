def get_on_failed_code_submission_text(output_data):
    if output_data.failed_test_idx == -1:
        return (
            'Решение не прошло проверку, попробуйте еще раз\n\n'
            f'```\n{output_data.failed_output[:500] + '...'}```'
        )
    return (
        'Решение не прошло проверку, попробуйте еще раз\n\n'
        f'Тест #{output_data.failed_test_idx + 1} провалился:\n'
        f'```\n{output_data.failed_output}```'
    )
