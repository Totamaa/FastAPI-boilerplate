from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.core.api.router import router_api
from app.core.config.logs import get_logger
from app.core.config.settings import get_settings
from app.core.errors.exceptions.base import AppException
from app.core.errors.handlers.business import handle_business_exceptions
from app.core.errors.handlers.catchall import handle_generic_exceptions
from app.core.errors.handlers.db import handle_db_exceptions
from app.core.health.router import health_router
from app.core.middleware.headers import add_global_headers
from app.core.middleware.rate_limit import rate_limiter


def create_app() -> FastAPI:

    logger = get_logger()
    settings = get_settings()

    docs_url = redoc_url = openapi_url = None

    if settings.ENVIRONMENT != "prod":
        docs_url = "/api/docs"
        redoc_url = "/api/redoc"
        openapi_url = "/api/openapi.json"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("SYSTEM:Startup", "Backend started")
        yield
        logger.info("SYSTEM:Shutdown", "Backend stopped")

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
        swagger_ui_init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,  # ex: ["*"] or ["https://frontend.com"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(add_global_headers)
    app.middleware("http")(rate_limiter)

    app.add_exception_handler(AppException, handle_business_exceptions)
    app.add_exception_handler(SQLAlchemyError, handle_db_exceptions)
    app.add_exception_handler(Exception, handle_generic_exceptions)

    app.include_router(health_router)
    app.include_router(router_api, prefix="/api")

    return app


app = create_app()
