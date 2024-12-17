from dataclasses import dataclass


@dataclass(frozen=True)
class Pagination:
    offset: int | None = None
    limit: int | None = None


# special sentinel object which used in a situation when None might be a useful value
UNSET: str = 'UNSET'
