from abc import abstractmethod
from typing import Protocol


class Commiter(Protocol):
    @abstractmethod
    def commit(self):
        raise NotImplementedError
