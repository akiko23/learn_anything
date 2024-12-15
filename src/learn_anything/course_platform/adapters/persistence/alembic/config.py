import importlib

ALEMBIC_CONFIG = str(importlib.resources.path(
    'learn_anything.course_platform.adapters.persistence.alembic', 'alembic.ini',
).__enter__())
