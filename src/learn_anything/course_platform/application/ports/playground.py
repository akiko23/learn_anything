from dataclasses import dataclass
from typing import Protocol, Self, Any

from typing_extensions import NewType

StdOut = NewType('StdOut', str)
StdErr = NewType('StdErr', str)


@dataclass
class CodeIsInvalidError(Exception):
    code: str
    out: str
    err: str


class Playground(Protocol):
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(self, exc_type: type[Exception], exc_val: Any, exc_tb: str) -> None:
        raise NotImplementedError

    async def execute_code(self, code: str, raise_exc_on_err: bool = False) -> tuple[StdOut, StdErr]:
        raise NotImplementedError


class PlaygroundFactory(Protocol):
    def create(
            self,
            code_duration_timeout: int,
            identifier: str | None = None,
    ) -> Playground:
        raise NotImplementedError
