import uuid
from typing import Awaitable, Any, Callable

import aio_pika
import msgpack
from aio_pika.abc import AbstractChannel, ExchangeType
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update
from dishka import AsyncContainer

from learn_anything.api_gateway.adapters.logger import logger, correlation_id_ctx
from learn_anything.api_gateway.adapters.metrics import TOTAL_MESSAGES_PRODUCED


class SendToQueueMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer):
        self._container = container

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Any:
        async with self._container(context={TelegramObject: event}) as request_container:
            channel = await request_container.get(AbstractChannel)
            queue_name = 'tg_updates'

            exchange = await channel.declare_exchange("tg_updates", ExchangeType.TOPIC, durable=True)
            queue = await channel.declare_queue(name=queue_name, durable=True)
            await queue.bind(
                exchange,
                queue_name,
            )

            correlation_id = str(uuid.uuid4())
            correlation_id_ctx.set(correlation_id)

            logger.info('Sending update to a queue..')
            await exchange.publish(
                message=aio_pika.Message(
                    body=msgpack.packb(event.model_dump()),
                    correlation_id=correlation_id
                ),
                routing_key=queue_name,
            )
            TOTAL_MESSAGES_PRODUCED.inc()
