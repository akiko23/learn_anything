from collections.abc import Sequence, Iterable
from typing import Protocol, Self

from learn_anything.entities.task.models import CodeTask, CodeTaskTest
from learn_anything.entities.user.models import UserID


class Playground(Protocol):
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    async def execute_code(self, code: str) -> (str, str):
        raise NotImplementedError


class PlaygroundFactory(Protocol):
    def create(
            self,
            code_duration_timeout: int,
            identifier: str | None = None,
    ) -> Playground:
        raise NotImplementedError

