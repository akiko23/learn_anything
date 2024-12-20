from dataclasses import dataclass

import toml


@dataclass
class BotConfig:
    token: str


def load_bot_config(config_path: str) -> BotConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['bot']

    config = BotConfig(**data)
    return config
