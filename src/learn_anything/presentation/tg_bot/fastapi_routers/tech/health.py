from fastapi import APIRouter
from starlette.responses import Response

router = APIRouter()

@router.get("/healthcheck")
async def healthcheck() -> Response:
    return Response("Healthy", status_code=200)
