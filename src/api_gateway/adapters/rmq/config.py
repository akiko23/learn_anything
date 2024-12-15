from dataclasses import dataclass

import toml


@dataclass
class RMQConfig:
    host: str
    port: int
    user: str
    password: str
    pool_size: int = 10

    @property
    def uri(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


def load_rmq_config(config_path: str = '.configs/app.toml') -> RMQConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['rmq']

    config = RMQConfig(**data)
    return config

