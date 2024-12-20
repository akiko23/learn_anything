from dataclasses import dataclass
from typing import Optional

import toml


@dataclass
class BotConfig:
    token: str
    bot_webhook_url: Optional[str] = None


def load_bot_config(config_path: str) -> BotConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['bot']

    config = BotConfig(**data)
    return config
