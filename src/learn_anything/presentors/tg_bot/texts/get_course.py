from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData
from learn_anything.application.interactors.course.get_many_courses import CourseData


def get_single_course_text(course_data: GetFullCourseOutputData):
    registered_text = ''
    if course_data.user_is_registered:
        registered_text = '\n📝Вы записаны\n'

    if course_data.registrations_limit:
        registrations_left = course_data.registrations_limit - course_data.total_registered
        if registrations_left > 0:
            registrations_left_text = f"Осталось {registrations_left} мест"

    return f"""{course_data.title}

Описание: {course_data.description}

Автор: {course_data.creator.title()}

Зарегестрировано: {course_data.total_registered}
{registered_text}
Создан: {course_data.created_at}
"""