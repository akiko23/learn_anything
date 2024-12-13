import asyncio
from asyncio import Task
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.methods.base import TelegramMethod
from dishka.integrations.fastapi import inject, FromDishka
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

from learn_anything.presentation.bg_tasks import background_tasks

router = APIRouter()


@router.post("/webhook")
@inject
async def webhook(request: Request, dp: FromDishka[Dispatcher], bot: FromDishka[Bot]) -> JSONResponse:
    update = await request.json()

    task: Task[TelegramMethod[Any] | None] = asyncio.create_task(dp.feed_webhook_update(bot, update))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return ORJSONResponse({"status": "ok"})
