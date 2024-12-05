import dataclasses
import json
from datetime import datetime

from pydantic import BaseModel

from learn_anything.application.interactors.course.get_course import GetFullCourseOutputData
from learn_anything.application.interactors.course.get_many_courses import CourseData
from learn_anything.application.interactors.submission.get_many_submissions import SubmissionData
from learn_anything.application.interactors.task.get_course_tasks import TaskData
from learn_anything.application.ports.data.course_gateway import GetManyCoursesFilters
from learn_anything.application.ports.data.submission_gateway import GetManySubmissionsFilters


class DTOWrapperModel(BaseModel):
    dto: (
            CourseData | GetFullCourseOutputData | GetManyCoursesFilters |
            TaskData |
            SubmissionData | GetManySubmissionsFilters
    )


class DTOJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return str(o)

        if dataclasses.is_dataclass(o):
            model = DTOWrapperModel(dto=o)
            return model.model_dump()
        return super().default(o)


def dto_obj_hook(dct):
    encoded_dto = dct.get('dto')
    if encoded_dto:
        return DTOWrapperModel.model_validate(dct).dto
    return dct
