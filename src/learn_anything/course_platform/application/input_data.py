from dataclasses import dataclass
from typing import Any
from unittest.mock import sentinel


@dataclass(frozen=True)
class Pagination:
    offset: int | None = None
    limit: int | None = None


# special sentinel object which used in a situation when None might be a useful value
UNSET: str = 'UNSET'
