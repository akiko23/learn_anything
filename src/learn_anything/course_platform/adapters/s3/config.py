from dataclasses import dataclass

import toml


@dataclass
class S3Config:
    endpoint_url: str
    access_key: str
    secret_key: str


def load_s3_config(config_path: str) -> S3Config:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)['s3']

    config = S3Config(**data)
    return config
