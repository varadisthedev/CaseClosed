from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EvidenceRequestStatus, EvidenceRequestType, EvidenceSource
from app.db.models.base import Base, TimestampMixin


def _pg_enum(enum_cls, name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in e],
        native_enum=True,
    )


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    claim: Mapped[str] = mapped_column(Text)
    source: Mapped[EvidenceSource] = mapped_column(
        _pg_enum(EvidenceSource, "evidence_source")
    )
    ref: Mapped[str] = mapped_column(String(255), default="")
    entity_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)

    case: Mapped["Case"] = relationship(back_populates="evidence")


class EvidenceRequest(Base, TimestampMixin):
    __tablename__ = "evidence_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    type: Mapped[EvidenceRequestType] = mapped_column(
        _pg_enum(EvidenceRequestType, "evidence_request_type")
    )
    asked_after_step: Mapped[int] = mapped_column(Integer, default=0)
    assumed_response: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[EvidenceRequestStatus] = mapped_column(
        _pg_enum(EvidenceRequestStatus, "evidence_request_status"),
        default=EvidenceRequestStatus.PENDING,
    )

    case: Mapped["Case"] = relationship(back_populates="evidence_requests")
