from typing import Callable, Coroutine, Awaitable

from learn_anything.api_gateway.adapters.metrics import REQUESTS_TOTAL
from fastapi import Request, Response

class RequestCountMiddleware:
    async def __call__(
            self,
            request: Request,
            call_next: Callable[[Request], Coroutine[Awaitable[Response], None, Response]]
    ) -> Response:
        REQUESTS_TOTAL.labels(method=request.method, path=request.url.path).inc()
        response = await call_next(request)
        return response
