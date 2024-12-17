import asyncio
import logging
import sys
from asyncio.exceptions import CancelledError
from logging import StreamHandler, Formatter

import alembic.config

from learn_anything.course_platform.adapters.persistence.alembic.config import ALEMBIC_CONFIG

from learn_anything.api_gateway.main.tg_bot import main as api_gateway_entry_point
from learn_anything.course_platform.main.tg_updates_consumer import main as consumer_entry_point


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
    # starts both: api gateway and consumer
    if argv[0] == 'bot':
        try:
            logger.info('Starting services from cli..')

            asyncio.run(_run_services())
        except (KeyboardInterrupt, SystemExit, CancelledError, RuntimeError):
            logger.exception("Bot was interrupted with err!")
        else:
            logger.info("Bot was successfully stopped")

    elif argv[0] == 'consumer':
        try:
            logger.info('Starting consumer from cli..')
            asyncio.run(consumer_entry_point())
        except (KeyboardInterrupt, SystemExit, CancelledError):
            logger.exception("Consumer was interrupted with err!")
        else:
            logger.info("Consumer was successfully stopped")

    elif argv[0] == 'api_gateway':
        try:
            logger.info('Starting api_gateway from cli..')
            asyncio.run(api_gateway_entry_point())
        except (KeyboardInterrupt, SystemExit, CancelledError):
            logger.exception("API gateway was interrupted with err!")
        else:
            logger.info("API gateway was successfully stopped")


async def _run_services():
    await asyncio.gather(
        api_gateway_entry_point(),
        consumer_entry_point(),
    )


def main():
    command = sys.argv[1]
    match command:
        case 'alembic':
            alembic_handler(sys.argv[2:])

        case 'start':
            command_start_handler(sys.argv[2:])
