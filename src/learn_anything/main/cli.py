import asyncio
import logging
import sys
from asyncio.exceptions import CancelledError
from logging import StreamHandler, Formatter

import alembic.config
import uvicorn

from learn_anything.course_platform.adapters.persistence.alembic.config import ALEMBIC_CONFIG

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
        import uvicorn

        try:
            logger.info('Starting consumer from cli..')
            uvicorn_config = uvicorn.Config(
                'learn_anything.main.consumer:create_app',
                factory=True,
                host='0.0.0.0',
                port=8081,
                workers=1
            )
            server = uvicorn.Server(uvicorn_config)
            asyncio.run(server.serve())
        except (KeyboardInterrupt, SystemExit, CancelledError):
            logger.exception("Consumer was interrupted with err!")
        else:
            logger.info("Consumer was successfully stopped")

    elif argv[0] == 'api_gateway':
        import uvicorn

        try:
            logger.info('Starting consumer from cli..')
            uvicorn_config = uvicorn.Config(
                'learn_anything.main.consumer:create_app',
                factory=True,
                host='0.0.0.0',
                port=8081,
                workers=1
            )
            server = uvicorn.Server(uvicorn_config)
            asyncio.run(server.serve())
        except (KeyboardInterrupt, SystemExit, CancelledError):
            logger.exception("Consumer was interrupted with err!")
        else:
            logger.info("Consumer was successfully stopped")


async def _run_services():
    api_gateway_uvicorn_config = uvicorn.Config(
        'learn_anything.api_gateway.main.tg_bot:create_app',
        factory=True,
        host='0.0.0.0',
        port=8080,
        workers=1
    )
    api_gateway_server = uvicorn.Server(api_gateway_uvicorn_config)

    consumer_uvicorn_config = uvicorn.Config(
        'learn_anything.course_platform.main.consumer:create_app',
        factory=True,
        host='0.0.0.0',
        port=8081,
        workers=1
    )
    consumer_server = uvicorn.Server(consumer_uvicorn_config)

    serve_api_gateway_task = asyncio.create_task(api_gateway_server.serve())
    serve_consumer_task = asyncio.create_task(consumer_server.serve())

    await asyncio.gather(
            serve_consumer_task,
            serve_api_gateway_task,
    )



def main():
    command = sys.argv[1]
    match command:
        case 'alembic':
            alembic_handler(sys.argv[2:])

        case 'start':
            command_start_handler(sys.argv[2:])
