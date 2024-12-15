from functools import partial

import aio_pika
from aio_pika import Connection
from aio_pika.abc import AbstractRobustConnection, AbstractChannel
from aio_pika.pool import Pool

from api_gateway.adapters.rmq.config import RMQConfig


async def get_channel(connection_pool: Pool[Connection]) -> AbstractChannel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


async def get_connection_pool(rmq_cfg: RMQConfig) -> Pool[Connection]:
    return Pool(partial(_get_connection, rmq_cfg), max_size=rmq_cfg.pool_size)


async def _get_connection(rmq_cfg: RMQConfig) -> AbstractRobustConnection:
    return await aio_pika.connect_robust(rmq_cfg.uri)
