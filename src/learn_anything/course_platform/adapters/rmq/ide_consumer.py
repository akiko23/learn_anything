"""
Consumer for IDE submissions queue.
Reads code submission from RMQ, runs it through the playground, writes result to Redis.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import cast

import msgpack
import redis.asyncio as aioredis
from aio_pika.abc import AbstractIncomingMessage

from learn_anything.course_platform.adapters.playground.unix_playground import VirtualMachinePool, UnixPlayground
from learn_anything.course_platform.adapters.rmq.ide_submissions import IDE_SUBMISSIONS_QUEUE, IDE_RESULT_TTL
from learn_anything.course_platform.application.ports.playground import StdErr, StdOut

logger = logging.getLogger(__name__)

RESULT_KEY_PREFIX = "ide_result:"


def _result_key(submission_id: str) -> str:
    return f"{RESULT_KEY_PREFIX}{submission_id}"


async def process_ide_submission(
    msg: AbstractIncomingMessage,
    redis_client: aioredis.Redis,  # type: ignore[type-arg]
    vm_pool: VirtualMachinePool,
) -> None:
    """Process a single IDE submission message."""
    payload = msgpack.unpackb(msg.body)
    submission_id: str = payload["submission_id"]
    task_id: int = payload["task_id"]
    user_id: int = payload["user_id"]
    code: str = payload["code"]
    prepared_code: str | None = payload.get("prepared_code")
    tests: list[dict[str, str]] = payload.get("tests", [])
    code_duration_timeout: int = payload.get("code_duration_timeout", 10)

    logger.info(
        "Processing IDE submission %s for task=%s user=%s",
        submission_id, task_id, user_id,
    )

    result: dict[str, object]
    try:
        full_code = code
        if prepared_code:
            full_code = prepared_code + "\n" + code

        async with UnixPlayground(
            identifier=f"ide_{user_id}_{task_id}",
            code_duration_timeout=code_duration_timeout,
            vm_pool=vm_pool,
        ) as pl:
            out, err = await pl.execute_code(code=full_code)

            if err:
                result = {
                    "status": "error",
                    "output": str(out),
                    "error": str(err),
                    "failed_test": None,
                }
            else:
                user_output = str(out)
                failed_test: dict[str, object] | None = None

                for idx, test in enumerate(tests):
                    test_code = (
                        f"{full_code}\n"
                        f"stdout = '''{user_output}'''\n"
                        f"stderr = ''\n"
                        + test["code"]
                    )
                    test_out, test_err = await pl.execute_code(code=test_code)
                    if test_err:
                        failed_test = {
                            "index": idx,
                            "output": str(test_err).strip(),
                        }
                        break

                if failed_test:
                    result = {
                        "status": "failed",
                        "output": user_output,
                        "error": None,
                        "failed_test": failed_test,
                    }
                else:
                    result = {
                        "status": "ok",
                        "output": user_output,
                        "error": None,
                        "failed_test": None,
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
    vm_pool: VirtualMachinePool,
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
                vm_pool,
            )
        )
