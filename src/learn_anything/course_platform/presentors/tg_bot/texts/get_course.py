from learn_anything.course_platform.application.interactors.course.get_course import GetFullCourseOutputData
from learn_anything.course_platform.presentors.tg_bot.texts.formatters import format_time, format_date


def get_single_course_text(course_data: GetFullCourseOutputData) -> str:
    registered_text = ''
    if course_data.user_is_registered:
        registered_text = '\n📝Вы записаны\n'

    registrations_left_text = ''
    if course_data.registrations_limit:
        registrations_left = course_data.registrations_limit - course_data.total_registered
        if registrations_left > 0:
            registrations_left_text = f"\nОсталось {registrations_left} мест\n"

    return f"""{course_data.title}

Описание: {course_data.description}

Автор: {course_data.creator.title()}
{registered_text}
👤{course_data.total_registered}
{registrations_left_text}
Всего заданий: {course_data.total_tasks}

🕓{format_time(total_tasks=course_data.total_tasks)}

Создан: {format_date(course_data.created_at)}
Обновлен: {format_date(course_data.updated_at)}
"""
