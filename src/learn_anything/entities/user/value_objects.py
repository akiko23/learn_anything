from dataclasses import dataclass

from learn_anything.entities.user.errors import UsernameToShortError


@dataclass
class Username:
    username: str

    def __post_init__(self) -> None:
        if len(self.username) <= 5:
            raise UsernameToShortError(self.username)
