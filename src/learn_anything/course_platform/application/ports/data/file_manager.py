import io
from typing import Protocol, NewType

COURSES_DEFAULT_DIRECTORY = 'courses'

DirTree = NewType("DirTree", tuple[str])
FilePath = NewType("FilePath", str)


class FileManager(Protocol):
    async def save(self, payload: bytes, file_path: FilePath) -> None:
        raise NotImplementedError

    async def update(self, old_file_path: FilePath, new_file_path: FilePath, payload: bytes | None) -> None:
        raise NotImplementedError

    # defines FS specific path format
    def generate_path(self, directories: tuple[str] | str, filename: str) -> FilePath:
        raise NotImplementedError

    async def get_props_by_path(self, path: FilePath) -> tuple[DirTree, str]:
        raise NotImplementedError

    async def get_by_file_path(self, file_path: FilePath) -> io.IOBase | None:
        raise NotImplementedError

    async def delete(self, file_path: FilePath) -> None:
        raise NotImplementedError

    async def delete_folder(self, name: str) -> None:
        raise NotImplementedError
