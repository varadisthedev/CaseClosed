from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import engine
from app.api.routes import cases, investigation, risk, actions, agent


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)
    logger.info("Starting CaseClosed API", env=settings.APP_ENV)
    yield
    await engine.dispose()
    logger.info("Shutting down CaseClosed API")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CaseClosed API",
        description="Agentic Fraud Investigation System",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.APP_ENV == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
    app.include_router(investigation.router, prefix="/api/cases", tags=["investigation"])
    app.include_router(risk.router, prefix="/api/cases", tags=["risk"])
    app.include_router(actions.router, prefix="/api/cases", tags=["actions"])
    app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "caseclosed-api"}

    return app


app = create_app()