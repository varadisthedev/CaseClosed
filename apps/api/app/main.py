from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import actions, agent, cases, investigation, risk
from app.core.config import get_settings
from app.core.context import new_request_id, set_request_id
from app.core.errors import AppError
from app.core.logging import configure_logging, get_logger
from app.db.session import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)
    init_db()
    logger.info("Starting CaseClosed API", env=settings.APP_ENV)
    yield
    logger.info("Shutting down CaseClosed API")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Agentic Fraud Investigation System",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    )

    origins = settings.cors_origins_list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or new_request_id()
        set_request_id(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    register_error_handlers(app)

    app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
    app.include_router(
        investigation.router, prefix="/api/cases", tags=["investigation"]
    )
    app.include_router(risk.router, prefix="/api/cases", tags=["risk"])
    app.include_router(actions.router, prefix="/api/cases", tags=["actions"])
    app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

    @app.get("/health", tags=["system"])
    async def health_check():
        return {
            "status": "healthy",
            "service": "caseclosed-api",
            "version": settings.APP_VERSION,
        }

    return app


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError):
        from app.core.context import get_request_id

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "code": exc.code,
                "detail": exc.detail,
                "request_id": get_request_id(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, exc: RequestValidationError):
        from app.core.context import get_request_id

        return JSONResponse(
            status_code=422,
            content={
                "error": "Request validation failed",
                "code": "validation_error",
                "detail": {"errors": exc.errors()},
                "request_id": get_request_id(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception):
        from app.core.context import get_request_id

        logger.error("Unhandled error", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "code": "internal_error",
                "detail": {},
                "request_id": get_request_id(),
            },
        )


app = create_app()