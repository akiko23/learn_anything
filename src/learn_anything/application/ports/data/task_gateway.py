from typing import Protocol, Sequence

from learn_anything.entities.course.models import CourseID
from learn_anything.entities.task.models import TaskID, Task, CodeTask, PollTask, TextInputTask


class TaskGateway(Protocol):
    async def with_id(self, task_id: TaskID) -> Task:
        raise NotImplementedError

    async def get_code_task_with_id(self, task_id: TaskID) -> CodeTask:
        raise NotImplementedError

    async def get_poll_task_with_id(self, task_id: TaskID) -> PollTask:
        raise NotImplementedError

    async def get_text_input_task_with_id(self, task_id: TaskID) -> TextInputTask:
        raise NotImplementedError

    async def with_course(self, course_id: CourseID) -> Sequence[Task]:
        raise NotImplementedError

    # saves theory task
    async def save(self, task: Task) -> TaskID:
        raise NotImplementedError

    async def save_code_task(self, task: CodeTask) -> TaskID:
        raise NotImplementedError

    async def save_poll_task(self, task: PollTask) -> TaskID:
        raise NotImplementedError

    async def save_text_input_task(self, task: TextInputTask) -> TaskID:
        raise NotImplementedError
