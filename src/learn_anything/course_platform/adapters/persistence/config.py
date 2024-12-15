import os
from dataclasses import dataclass
import toml


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    db_name: str
    user: str
    password: str
    driver: str = 'asyncpg'

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}"
            f"/{self.db_name}"
        )


def load_db_config(config_path: str) -> DatabaseConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['db']

    config = DatabaseConfig(**data)
    return config
