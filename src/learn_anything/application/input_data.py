from dataclasses import dataclass


@dataclass(frozen=True)
class Pagination:
    offset: int | None = None
    limit: int | None = None
