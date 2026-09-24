from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EvidenceRequestStatus, EvidenceRequestType, EvidenceSource
from app.db.models.base import Base, TimestampMixin, portable_enum


class Evidence(Base, TimestampMixin):
    """A single piece of investigation evidence with provenance.

    ``source`` distinguishes real sources (``tigergraph``, ``ml_model``,
    ``llm``, ``document``, ``customer``, ``external``) from ``placeholder``.
    """

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(48), default="graph")
    claim: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(32), default="placeholder")
    source_ref: Mapped[str] = mapped_column(String(255), default="")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    entity_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    as_of: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    provisional: Mapped[bool] = mapped_column(Boolean, default=True)

    case: Mapped["Case"] = relationship(back_populates="evidence")


class EvidenceRequest(Base, TimestampMixin):
    __tablename__ = "evidence_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    type: Mapped[EvidenceRequestType] = mapped_column(
        portable_enum(EvidenceRequestType, "evidence_request_type")
    )
    asked_after_step: Mapped[int] = mapped_column(Integer, default=0)
    assumed_response: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[EvidenceRequestStatus] = mapped_column(
        portable_enum(EvidenceRequestStatus, "evidence_request_status"),
        default=EvidenceRequestStatus.PENDING,
    )

    case: Mapped["Case"] = relationship(back_populates="evidence_requests")