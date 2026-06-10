"""
IDE submission consumer — reads from `ide_submissions` queue and writes result to Redis.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

import aio_pika
import msgpack
from aio_pika.abc import AbstractChannel, ExchangeType

if TYPE_CHECKING:
    import redis.asyncio as aioredis

IDE_SUBMISSIONS_QUEUE = "ide_submissions"
IDE_RESULT_TTL = 300  # 5 minutes


@dataclass
class IdeSubmissionMessage:
    submission_id: str
    task_id: int
    user_id: int
    code: str


async def publish_ide_submission(
    channel: AbstractChannel,
    task_id: int,
    user_id: int,
    code: str,
    prepared_code: str | None = None,
    tests: list[dict[str, str]] | None = None,
    code_duration_timeout: int = 10,
) -> str:
    """Publish an IDE submission to RMQ. Returns submission_id."""
    submission_id = str(uuid.uuid4())

    msg = IdeSubmissionMessage(
        submission_id=submission_id,
        task_id=task_id,
        user_id=user_id,
        code=code,
    )

    exchange = await channel.declare_exchange(
        IDE_SUBMISSIONS_QUEUE, ExchangeType.TOPIC, durable=True
    )
    queue = await channel.declare_queue(name=IDE_SUBMISSIONS_QUEUE, durable=True)
    await queue.bind(exchange, IDE_SUBMISSIONS_QUEUE)

    await exchange.publish(
        message=aio_pika.Message(
            body=msgpack.packb(
                {
                    "submission_id": msg.submission_id,
                    "task_id": msg.task_id,
                    "user_id": msg.user_id,
                    "code": msg.code,
                    "prepared_code": prepared_code,
                    "tests": tests or [],
                    "code_duration_timeout": code_duration_timeout,
                }
            ),
        ),
        routing_key=IDE_SUBMISSIONS_QUEUE,
    )
    return submission_id
