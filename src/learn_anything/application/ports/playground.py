from dataclasses import dataclass
from typing import Protocol, Self

from typing_extensions import TypeVar

StdOut = TypeVar('StdOut', bound=str, contravariant=True)
StdErr = TypeVar('StdErr', bound=str, contravariant=True)


@dataclass
class CodeIsInvalidError(Exception):
    code: str
    out: str
    err: str


class Playground(Protocol):
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    async def execute_code(self, code: str, raise_exc_on_err: bool = False) -> (StdOut, StdErr):
        raise NotImplementedError


class PlaygroundFactory(Protocol):
    def create(
            self,
            code_duration_timeout: int,
            identifier: str | None = None,
    ) -> Playground:
        raise NotImplementedError
