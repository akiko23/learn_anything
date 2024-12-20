from typing import Protocol
from uuid import UUID


class TokenProcessor(Protocol):
    def encode(self, subject: str) -> str:
        raise NotImplementedError

    def decode(self, token: str) -> UUID:
        raise NotImplementedError
