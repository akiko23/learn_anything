from dataclasses import dataclass

import toml


@dataclass
class WebConfig:
    title: str
    description: str
    host: str
    port: int
    log_level: str = "info"


def load_web_config(config_path: str) -> WebConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['web']

    config = WebConfig(**data)
    return config
