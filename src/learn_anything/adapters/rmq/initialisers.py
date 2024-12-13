from aio_pika import ExchangeType, Connection
from aio_pika.pool import Pool


async def init_rabbitmq(connection_pool: Pool[Connection]):
    async with connection_pool.acquire() as connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange("user_submissions", ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue('user_messages', durable=True)
        await queue.bind(exchange, 'user_messages')
