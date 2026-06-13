from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config.logs import get_logger
from app.core.health.checks import check_db, check_redis, compute_overall_status

health_router = APIRouter(tags=["Health"])
logger = get_logger()


@health_router.get("/health/live")
async def liveness() -> dict:
    return {"status": "ok"}


async def _run_checks() -> tuple[dict, str]:
    checks = {
        "db": await check_db(),
        "redis": await check_redis(),
    }
    overall = compute_overall_status(checks)
    return checks, overall


@health_router.get("/health/ready")
async def readiness() -> JSONResponse:
    checks, overall = await _run_checks()
    status_code = 200 if overall == "ok" else 503
    if overall != "ok":
        logger.warning("HEALTH:Readiness", f"Status is {overall}", extra=str(checks))
    return JSONResponse(
        status_code=status_code,
        content={"status": overall, "checks": checks},
    )


@health_router.get("/health")
async def health() -> JSONResponse:
    checks, overall = await _run_checks()
    status_code = 200 if overall == "ok" else 503
    if overall != "ok":
        logger.warning("HEALTH:Status", f"Status is {overall}", extra=str(checks))
    return JSONResponse(
        status_code=status_code,
        content={"status": overall, "checks": checks},
    )
