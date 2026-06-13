"""
Consumer for IDE submissions queue.
Reads code submission from RMQ, runs it through the interactor, writes result to Redis.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import cast

import msgpack
import redis.asyncio as aioredis
from aio_pika.abc import AbstractIncomingMessage
from dishka import AsyncContainer

from learn_anything.course_platform.adapters.rmq.ide_submissions import IDE_SUBMISSIONS_QUEUE, IDE_RESULT_TTL

logger = logging.getLogger(__name__)

RESULT_KEY_PREFIX = "ide_result:"


def _result_key(submission_id: str) -> str:
    return f"{RESULT_KEY_PREFIX}{submission_id}"


async def process_ide_submission(
    msg: AbstractIncomingMessage,
    redis_client: aioredis.Redis,  # type: ignore[type-arg]
    container: AsyncContainer,
) -> None:
    """Process a single IDE submission message."""
    payload = msgpack.unpackb(msg.body)
    submission_id: str = payload["submission_id"]
    task_id: int = payload["task_id"]
    user_id: int = payload["user_id"]
    code: str = payload["code"]

    logger.info(
        "Processing IDE submission %s for task=%s user=%s",
        submission_id, task_id, user_id,
    )

    result: dict[str, object]
    try:
        from learn_anything.course_platform.application.interactors.submission.create_submission import (
            CreateCodeTaskSubmissionInteractor,
            CreateCodeTaskSubmissionInputData,
        )

        async with container() as request_container:
            interactor = await request_container.get(CreateCodeTaskSubmissionInteractor)
            output_data = await interactor.execute(
                data=CreateCodeTaskSubmissionInputData(
                    task_id=task_id,
                    submission=code,
                )
            )

        if output_data.failed_test is None:
            result = {
                "status": "ok",
                "output": "",
                "error": None,
                "failed_test": None,
            }
        elif output_data.failed_test.failed_test_idx == -1:
            result = {
                "status": "error",
                "output": "",
                "error": output_data.failed_test.failed_test_output,
                "failed_test": None,
            }
        else:
            result = {
                "status": "failed",
                "output": "",
                "error": None,
                "failed_test": {
                    "index": output_data.failed_test.failed_test_idx,
                    "output": output_data.failed_test.failed_test_output,
                },
            }
    except Exception as exc:
        logger.exception("Error processing IDE submission %s: %s", submission_id, exc)
        result = {
            "status": "error",
            "output": "",
            "error": str(exc),
            "failed_test": None,
        }

    # Write result to Redis with TTL
    key = _result_key(submission_id)
    await redis_client.setex(key, IDE_RESULT_TTL, json.dumps(result))
    logger.info("Wrote IDE result for submission %s → %s", submission_id, result["status"])

    await msg.ack()


async def start_ide_consumer(
    channel: object,
    redis_client: aioredis.Redis,  # type: ignore[type-arg]
    container: AsyncContainer,
) -> None:
    """Start consuming ide_submissions queue. Runs indefinitely."""
    from aio_pika.abc import AbstractChannel, ExchangeType  # local import to avoid circular

    ch = cast("AbstractChannel", channel)  # type: ignore[type-arg]
    exchange = await ch.declare_exchange(IDE_SUBMISSIONS_QUEUE, ExchangeType.TOPIC, durable=True)
    queue = await ch.declare_queue(name=IDE_SUBMISSIONS_QUEUE, durable=True)
    await queue.bind(exchange, IDE_SUBMISSIONS_QUEUE)
    await ch.set_qos(prefetch_count=5)

    logger.info("Starting IDE submissions consumer…")
    async for message in queue.iterator():
        asyncio.create_task(
            process_ide_submission(
                cast(AbstractIncomingMessage, message),
                redis_client,
                container,
            )
        )
