import sys

import alembic.config

from learn_anything.adapters.persistence.alembic.config import ALEMBIC_CONFIG


def alembic_handler(argv):
    alembic.config.main(
        prog='learn-anything alembic',
        argv=['-c', ALEMBIC_CONFIG, *argv],
    )


def main():
    command = sys.argv[1]
    match command:
        case 'alembic':
            alembic_handler(sys.argv[2:])
