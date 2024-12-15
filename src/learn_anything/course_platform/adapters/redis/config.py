from dataclasses import dataclass

import toml


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379

    @property
    def dsn(self) -> str:
        return f"redis://{self.host}:{self.port}/0"


def load_redis_config(config_path: str) -> RedisConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['redis']

    config = RedisConfig(**data)
    return config
