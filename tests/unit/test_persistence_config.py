import tempfile
from pathlib import Path

import pytest

from learn_anything.course_platform.adapters.persistence.config import (
    DatabaseConfig,
    load_db_config,
)


def test_load_db_config():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""
[db]
user = "testuser"
password = "testpass"
db_name = "testdb"
host = "localhost"
port = 5433
""")
        path = f.name
    try:
        cfg = load_db_config(path)
        assert cfg.user == "testuser"
        assert cfg.password == "testpass"
        assert cfg.db_name == "testdb"
        assert cfg.host == "localhost"
        assert cfg.port == 5433
        assert cfg.driver == "asyncpg"
    finally:
        Path(path).unlink(missing_ok=True)


def test_database_config_db_url():
    cfg = DatabaseConfig(
        host="h",
        port=5432,
        db_name="d",
        user="u",
        password="p",
    )
    assert "postgresql+asyncpg://u:p@h:5432/d" == cfg.db_url
