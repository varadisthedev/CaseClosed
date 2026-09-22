from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import get_settings


def create_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.APP_ENV == "development",
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


engine = create_engine()
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()