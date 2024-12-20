import dataclasses
import json
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from learn_anything.course_platform.application.interactors.course.get_course import GetFullCourseOutputData
from learn_anything.course_platform.application.interactors.course.get_many_courses import CourseData
from learn_anything.course_platform.application.interactors.submission.get_many_submissions import SubmissionData
from learn_anything.course_platform.application.interactors.task.get_course_tasks import CodeTaskData, TheoryTaskData
from learn_anything.course_platform.application.ports.data.course_gateway import GetManyCoursesFilters
from learn_anything.course_platform.application.ports.data.submission_gateway import GetManySubmissionsFilters

camel_to_snake_pattern = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

DTOS = [
    camel_to_snake_pattern.sub('_', tp.__name__).lower()
    for tp in [
        CourseData, GetFullCourseOutputData, GetManyCoursesFilters,
        CodeTaskData, TheoryTaskData,
        SubmissionData, GetManySubmissionsFilters,
    ]
]


class DTOWrapperModel(BaseModel):
    course_data: CourseData | None = Field(default=None)
    get_full_course_output_data: GetFullCourseOutputData | None = Field(default=None)
    get_many_courses_filters: GetManyCoursesFilters | None = Field(default=None)
    theory_task_data: TheoryTaskData | None = Field(default=None)
    code_task_data: CodeTaskData | None = Field(default=None)
    submission_data: SubmissionData | None = Field(default=None)
    get_many_submissions_filters: GetManySubmissionsFilters | None = Field(default=None)


class DTOJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return str(o)

        if dataclasses.is_dataclass(o):
            model = DTOWrapperModel()

            attr_name = camel_to_snake_pattern.sub('_', type(o).__name__).lower()
            setattr(model, attr_name, o)

            return model.model_dump(exclude_unset=True)
        return super().default(o)


def dto_obj_hook(dct: dict[str, Any]) -> Any:
    encoded_dto_name = ''
    for dto_attr_name in DTOS:
        if dct.get(dto_attr_name):
            encoded_dto_name = dto_attr_name

    if encoded_dto_name:
        s = DTOWrapperModel.model_validate(dct)
        return getattr(s, encoded_dto_name)
    return dct
