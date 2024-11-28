import asyncio
import logging
import sys
from logging import StreamHandler, Formatter

import alembic.config

from learn_anything.adapters.persistence.alembic.config import ALEMBIC_CONFIG

handler = StreamHandler()
handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s %(asctime)s: %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False


def alembic_handler(argv):
    alembic.config.main(
        prog='learn-anything alembic',
        argv=['-c', ALEMBIC_CONFIG, *argv],
    )


def command_start_handler(argv):
    if argv[0] == 'bot':
        from learn_anything.main.bot import main

        try:
            logger.info('Starting bot from cli..')
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            logger.exception("Bot was interrupted with err!")
        else:
            logger.info("Bot was successfully stopped")


def main():
    command = sys.argv[1]
    match command:
        case 'alembic':
            alembic_handler(sys.argv[2:])

        case 'start':
            command_start_handler(sys.argv[2:])
