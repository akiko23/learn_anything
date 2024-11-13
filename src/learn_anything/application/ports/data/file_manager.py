from typing import Protocol

import io

class FileManager(Protocol):
    def save(self, payload: bytes, file_path: str) -> None:
        raise NotImplementedError

    def get_by_file_path(self, file_path: str) -> io.IOBase | None:
        raise NotImplementedError

    def delete(self, file_path: str) -> None:
        raise NotImplementedError

    def delete_folder(self, name: str) -> None:
        raise NotImplementedError
