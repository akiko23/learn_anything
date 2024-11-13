from learn_anything.entities.task.models import PollTask, PollTaskOptionID, TextInputTask, TextInputTaskAnswer


def option_is_correct(task: PollTask, option_id: PollTaskOptionID):
    for option in task.options:
        if option.is_correct and option.id == option_id:
            return True
    return False


def answer_is_correct(task: TextInputTask, answer: TextInputTaskAnswer) -> bool:
    if answer in task.correct_answers:
        return True
    return False


