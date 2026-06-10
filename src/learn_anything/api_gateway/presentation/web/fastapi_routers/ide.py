"""
FastAPI router for the Python IDE WebApp.

Endpoints:
  GET  /ide                       — serve the IDE HTML page
  GET  /ide/task/{task_id}        — return task data as JSON
  POST /ide/submit                — accept code, verify Telegram initData, enqueue to RMQ
  GET  /ide/result/{submission_id} — polling: return result from Redis
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from urllib.parse import parse_qsl, unquote

import redis.asyncio as aioredis
from aio_pika.abc import AbstractChannel
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, ORJSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learn_anything.course_platform.adapters.persistence.tables import code_task_tests_table
from learn_anything.course_platform.adapters.persistence.tables.task import tasks_table
from learn_anything.course_platform.adapters.redis.config import RedisConfig
from learn_anything.course_platform.adapters.rmq.ide_submissions import (
    IDE_RESULT_TTL,
    publish_ide_submission,
)
from learn_anything.course_platform.domain.entities.task.models import CodeTask, CodeTaskTest

logger = logging.getLogger(__name__)

router = APIRouter()

# ── helpers ────────────────────────────────────────────────────────────────────

_BOT_TOKEN: str | None = None


def _get_bot_token() -> str:
    global _BOT_TOKEN
    if _BOT_TOKEN is None:
        # read from env or config path — injected at app startup
        _BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    return _BOT_TOKEN


def _verify_telegram_init_data(init_data: str, bot_token: str) -> dict[str, str] | None:
    """
    Verify Telegram WebApp initData HMAC and return parsed fields.
    Returns None if verification fails.
    """
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except Exception:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        return None

    return parsed


def _parse_user_from_init_data(parsed: dict[str, str]) -> int | None:
    try:
        user_obj = json.loads(parsed.get("user", "{}"))
        return int(user_obj.get("id", 0)) or None
    except (ValueError, TypeError):
        return None


# ── IDE page ───────────────────────────────────────────────────────────────────

_HTML_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "ide", "index.html")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def ide_page() -> HTMLResponse:
    """Serve the IDE HTML page."""
    with open(_HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)


# ── Task data endpoint ─────────────────────────────────────────────────────────

class TaskResponse(BaseModel):
    id: int
    title: str
    body: str
    prepared_code: str | None
    code_duration_timeout: int
    tests_count: int


@router.get("/task/{task_id}", response_model=TaskResponse)
@inject
async def get_task(
    task_id: int = Path(..., ge=1),
    session: FromDishka[AsyncSession] = ...,  # type: ignore[assignment]
) -> ORJSONResponse:
    """Return task metadata for the IDE."""
    stmt = select(CodeTask).where(tasks_table.c.id == task_id)
    result = await session.execute(stmt)
    task: CodeTask | None = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tests_stmt = select(CodeTaskTest).where(code_task_tests_table.c.task_id == task_id)
    tests_result = await session.execute(tests_stmt)
    tests = list(tests_result.scalars().all())

    return ORJSONResponse({
        "id": task_id,
        "title": task.title,
        "body": task.body,
        "prepared_code": task.prepared_code,
        "code_duration_timeout": task.code_duration_timeout or 10,
        "tests_count": len(tests),
    })


# ── Submit endpoint ────────────────────────────────────────────────────────────

class SubmitRequest(BaseModel):
    task_id: int
    code: str
    tg_init_data: str | None = None  # None allowed for dev/testing without Telegram


class SubmitResponse(BaseModel):
    submission_id: str


@router.post("/submit", response_model=SubmitResponse)
@inject
async def submit_code(
    body: SubmitRequest,
    session: FromDishka[AsyncSession] = ...,  # type: ignore[assignment]
    channel: FromDishka[AbstractChannel] = ...,  # type: ignore[assignment]
) -> ORJSONResponse:
    """
    Accept code submission, optionally verify Telegram initData,
    enqueue to RMQ, return submission_id for polling.
    """
    # Determine user_id
    user_id: int = 0
    bot_token = _get_bot_token()

    if body.tg_init_data and bot_token:
        parsed = _verify_telegram_init_data(body.tg_init_data, bot_token)
        if parsed is None:
            raise HTTPException(status_code=403, detail="Invalid Telegram initData")
        uid = _parse_user_from_init_data(parsed)
        if uid is None:
            raise HTTPException(status_code=403, detail="Could not parse user from initData")
        user_id = uid
    elif body.tg_init_data:
        logger.warning("BOT_TOKEN not set — skipping initData verification")

    # Load task to get prepared_code, tests, timeout
    stmt = select(CodeTask).where(tasks_table.c.id == body.task_id)
    result = await session.execute(stmt)
    task: CodeTask | None = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tests_stmt = select(CodeTaskTest).where(code_task_tests_table.c.task_id == body.task_id)
    tests_result = await session.execute(tests_stmt)
    tests = [{"code": t.code} for t in tests_result.scalars().all()]

    submission_id = await publish_ide_submission(
        channel=channel,
        task_id=body.task_id,
        user_id=user_id,
        code=body.code,
        prepared_code=task.prepared_code,
        tests=tests,
        code_duration_timeout=task.code_duration_timeout or 10,
    )

    return ORJSONResponse({"submission_id": submission_id})


# ── Result polling endpoint ────────────────────────────────────────────────────

@router.get("/result/{submission_id}")
@inject
async def get_result(
    submission_id: str = Path(..., min_length=1),
    redis_cfg: FromDishka[RedisConfig] = ...,  # type: ignore[assignment]
) -> ORJSONResponse:
    """Poll for IDE submission result. Returns 202 while pending, 200 when ready."""
    redis_client = aioredis.from_url(redis_cfg.dsn, decode_responses=True)
    try:
        key = f"ide_result:{submission_id}"
        raw = await redis_client.get(key)
    finally:
        await redis_client.aclose()

    if raw is None:
        return ORJSONResponse({"status": "pending"}, status_code=202)

    result = json.loads(raw)
    return ORJSONResponse(result, status_code=200)
