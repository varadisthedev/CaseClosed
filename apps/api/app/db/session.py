from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.models import Base

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _connect_args(url: str) -> dict:
    # SQLite needs check_same_thread disabled for FastAPI's threadpool.
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.SQL_ECHO,
            pool_pre_ping=not settings.DATABASE_URL.startswith("sqlite"),
            connect_args=_connect_args(settings.DATABASE_URL),
            future=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(), autoflush=True, expire_on_commit=False, future=True
        )
    return _session_factory


def init_db() -> None:
    """Create all tables. Alembic owns production migrations; this keeps
    dev/tests zero-config on SQLite."""
    Base.metadata.create_all(bind=get_engine())


def reset_engine() -> None:
    """Dispose and drop cached engine/factory (used by tests)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()