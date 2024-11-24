from learn_anything.application.interactors.course.get_many_courses import CourseData


def get_many_courses_text(course_data: CourseData):
    registered_text = ''
    if course_data.user_is_registered:
        registered_text = '\n📝Вы записаны\n'

    return f"""{course_data.title}

Описание: {course_data.description}

Автор: {course_data.creator.title()}

Зарегестрировано: {course_data.total_registered}
{registered_text}
Создан: {course_data.created_at}
"""