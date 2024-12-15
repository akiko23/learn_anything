from typing import Protocol

from typing_extensions import TypeVar

Payload = TypeVar('Payload')

class EventPublisher(Protocol):
    def publish(self, data: Payload) -> None:
        raise NotImplementedError
