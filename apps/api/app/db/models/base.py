from datetime import datetime

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def portable_enum(enum_cls, name: str) -> Enum:
    """Portable enum column.

    ``native_enum=False`` renders a VARCHAR + CHECK constraint on PostgreSQL
    and on SQLite, so the same schema runs on both without native PG types.
    Values (not member names) are persisted, e.g. ``risk_score``.
    """
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in e],
        native_enum=False,
        validate_strings=True,
    )