from typing import Protocol

import io

class FileManager(Protocol):
    def save(self, payload: bytes, path: str) -> None:
        pass

    def get_by_file_id(self, file_path: str) -> io.IOBase | None:
        pass

    def delete_object(self, path: str) -> None:
        pass
