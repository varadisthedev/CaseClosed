from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    CaseStatus,
    Pattern,
    PriorOutcome,
    TriggerType,
    Verdict,
)
from app.db.models.base import Base, TimestampMixin


def _pg_enum(enum_cls, name: str) -> Enum:
    """Store the enum *values* (e.g. 'risk_score') rather than member names."""
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in e],
        native_enum=True,
    )


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    trigger_type: Mapped[TriggerType] = mapped_column(
        _pg_enum(TriggerType, "trigger_type")
    )
    trigger_text: Mapped[str] = mapped_column(Text, default="")

    flagged_txn_id: Mapped[str] = mapped_column(String(32), index=True)
    card_id: Mapped[str] = mapped_column(String(32), index=True)
    customer_id: Mapped[str] = mapped_column(String(32), index=True)
    input_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[CaseStatus | None] = mapped_column(
        _pg_enum(CaseStatus, "case_status"), nullable=True
    )
    verdict: Mapped[Verdict | None] = mapped_column(
        _pg_enum(Verdict, "verdict"), nullable=True
    )
    fraud_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    pattern: Mapped[Pattern | None] = mapped_column(
        _pg_enum(Pattern, "pattern"), nullable=True
    )
    pattern_description: Mapped[str] = mapped_column(Text, default="")

    first_suspicious_txn_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    exposure_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")

    written_to_graph: Mapped[bool] = mapped_column(Boolean, default=False)
    graph_case_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    transactions: Mapped[list["CaseTransaction"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    connected_cards: Mapped[list["CaseConnectedCard"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    connected_devices: Mapped[list["CaseConnectedDevice"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    similar_cases: Mapped[list["CaseSimilarCase"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    evidence_requests: Mapped[list["EvidenceRequest"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    next_best_actions: Mapped[list["NextBestAction"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    action_executions: Mapped[list["ActionExecution"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    sar_report: Mapped["SarReport | None"] = relationship(
        back_populates="case", cascade="all, delete-orphan", uselist=False
    )


class CaseTransaction(Base, TimestampMixin):
    __tablename__ = "case_transactions"
    __table_args__ = (
        UniqueConstraint("case_id", "transaction_id", name="uq_case_transaction"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    transaction_id: Mapped[str] = mapped_column(String(32), index=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    amount_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="transactions")


class CaseConnectedCard(Base, TimestampMixin):
    __tablename__ = "case_connected_cards"
    __table_args__ = (
        UniqueConstraint("case_id", "card_id", name="uq_case_connected_card"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    card_id: Mapped[str] = mapped_column(String(32), index=True)
    reason: Mapped[str] = mapped_column(Text, default="")

    case: Mapped["Case"] = relationship(back_populates="connected_cards")


class CaseConnectedDevice(Base, TimestampMixin):
    __tablename__ = "case_connected_devices"
    __table_args__ = (
        UniqueConstraint("case_id", "device_profile", name="uq_case_connected_device"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    device_profile: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text, default="")

    case: Mapped["Case"] = relationship(back_populates="connected_devices")


class CaseSimilarCase(Base, TimestampMixin):
    __tablename__ = "case_similar_cases"
    __table_args__ = (
        UniqueConstraint(
            "case_id", "prior_case_id", name="uq_case_similar_prior_case"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    prior_case_id: Mapped[str] = mapped_column(String(32), index=True)
    similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, default="")

    case: Mapped["Case"] = relationship(back_populates="similar_cases")


class ClosedCase(Base, TimestampMixin):
    """Lightweight mirror of canonical closed cases for RAG/application state.

    Canonical closed-case graph data lives in TigerGraph (per decision).
    """

    __tablename__ = "closed_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(32), index=True)
    card_id: Mapped[str] = mapped_column(String(32), index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    outcome: Mapped[PriorOutcome] = mapped_column(
        _pg_enum(PriorOutcome, "prior_outcome")
    )
    pattern: Mapped[Pattern] = mapped_column(_pg_enum(Pattern, "pattern"))
    first_fraud_txn_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    txn_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    n_txns: Mapped[int] = mapped_column(Integer, default=0)
    exposure_usd: Mapped[float] = mapped_column(Float, default=0.0)
    connected_card_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    actions_taken: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    report_filed: Mapped[bool] = mapped_column(Boolean, default=False)
    analyst_notes: Mapped[str] = mapped_column(Text, default="")
