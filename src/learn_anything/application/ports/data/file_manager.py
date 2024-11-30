import io
from typing import Protocol, NewType

from typing_extensions import TypeVar

COURSES_DEFAULT_DIRECTORY = 'courses'

DirTree = NewType("DirTree", tuple[str])
FilePath = TypeVar("FilePath", bound=str)


# todo: add concurrency here
class FileManager(Protocol):
    def save(self, payload: bytes, file_path: str) -> None:
        raise NotImplementedError

    # defines FS specific path format
    def generate_path(self, directories: tuple[str], filename: str) -> FilePath:
        raise NotImplementedError

    def parse_path(self, path: FilePath) -> (DirTree, str):
        raise NotImplementedError

    def get_by_file_path(self, file_path: str) -> io.IOBase | None:
        raise NotImplementedError

    def delete(self, file_path: str) -> None:
        raise NotImplementedError

    def delete_folder(self, name: str) -> None:
        raise NotImplementedError
