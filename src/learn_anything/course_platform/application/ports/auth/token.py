from typing import Protocol, Any


class TokenProcessor(Protocol):
    def encode(self, subject: str) -> str:
        raise NotImplementedError

    def decode(self, token: str) -> str:
        raise NotImplementedError
