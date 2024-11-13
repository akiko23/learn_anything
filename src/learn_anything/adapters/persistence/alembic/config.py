import importlib

ALEMBIC_CONFIG = str(importlib.resources.path(
    'learn_anything.adapters.persistence.alembic', 'alembic.ini',
).__enter__())
