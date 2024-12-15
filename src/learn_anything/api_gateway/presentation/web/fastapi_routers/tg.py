import asyncio
from asyncio import Task
from typing import Any

import aio_pika
import msgpack
from aio_pika.abc import AbstractChannel, ExchangeType
from aiogram.methods.base import TelegramMethod
from dishka.integrations.fastapi import inject, FromDishka
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from learn_anything.api_gateway.adapters.logger import logger
from learn_anything.api_gateway.adapters.metrics import TOTAL_MESSAGES_PRODUCED
from learn_anything.course_platform.presentation.bg_tasks import background_tasks

router = APIRouter()


@router.post("/webhook")
@inject
async def webhook(request: Request, channel: FromDishka[AbstractChannel]) -> JSONResponse:
    update = await request.json()

    logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAaa')

    task: Task[TelegramMethod[Any] | None] = asyncio.create_task(_send_update_to_queue(channel, update))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return ORJSONResponse({"status": "ok"})


async def _send_update_to_queue(channel: AbstractChannel, update: dict[str, Any]):
    queue_name = 'tg_updates'

    logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAaa')

    exchange = await channel.declare_exchange("tg_updates", ExchangeType.TOPIC, durable=True)
    queue = await channel.declare_queue(name=queue_name, durable=True)
    await queue.bind(
        exchange,
        queue_name,
    )

    logger.info('Sending update to a queue..')
    await exchange.publish(
        message=aio_pika.Message(
            body=msgpack.packb(update),
            correlation_id=context.get(HeaderKeys.correlation_id)
        ),
        routing_key=queue_name,
    )
    TOTAL_MESSAGES_PRODUCED.inc()
