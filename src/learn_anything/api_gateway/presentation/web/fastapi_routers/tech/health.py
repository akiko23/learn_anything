
from fastapi import APIRouter
from starlette.responses import Response


router = APIRouter()


@router.get("/healthcheck")
async def healthcheck() -> Response:
    return Response("Healthy", status_code=200)


# @router.get("/s3-healthcheck")
# @inject
# async def healthcheck() -> Response:
#     cfg_path = os.getenv('COURSE_PLATFORM_CONFIG_PATH') or DEFAULT_COURSE_PLATFORM_CONFIG_PATH
#
#     s3_cfg = load_s3_config(cfg_path)
#     s3_resp = requests.get(s3_cfg.endpoint_url + "/minio/health/live")
#     if s3_resp.status_code == 200:
#         return Response("Healthy", status_code=200)
#     return Response(s3_resp.json(), status_code=500)
