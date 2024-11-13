from collections.abc import Sequence
from typing import Protocol, Self

from learn_anything.entities.task.models import CodeTask, CodeTaskTest
from learn_anything.entities.user.models import UserID


class Playground(Protocol):
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def check_submission(self) -> tuple[str, int]:
        raise NotImplementedError


class PlaygroundFactory(Protocol):
    def create(
            self,
            task: CodeTask,
            user_id: UserID,
            submission_content: str
    ) -> Playground:
        raise NotImplementedError

