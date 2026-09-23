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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    ActionPhase,
    ActionState,
    ActionType,
    ApprovalRoute,
)
from app.db.models.base import Base, TimestampMixin


def _pg_enum(enum_cls, name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in e],
        native_enum=True,
    )


class NextBestAction(Base, TimestampMixin):
    __tablename__ = "next_best_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    phase: Mapped[ActionPhase] = mapped_column(_pg_enum(ActionPhase, "action_phase"))
    action: Mapped[ActionType] = mapped_column(_pg_enum(ActionType, "action_type"))
    route: Mapped[ApprovalRoute] = mapped_column(
        _pg_enum(ApprovalRoute, "approval_route")
    )
    reason: Mapped[str] = mapped_column(Text, default="")
    policy_rule: Mapped[str] = mapped_column(String(16), default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    case: Mapped["Case"] = relationship(back_populates="next_best_actions")


class ActionExecution(Base, TimestampMixin):
    __tablename__ = "action_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    action: Mapped[ActionType] = mapped_column(_pg_enum(ActionType, "action_type"))
    route: Mapped[ApprovalRoute] = mapped_column(
        _pg_enum(ApprovalRoute, "approval_route")
    )
    state: Mapped[ActionState] = mapped_column(
        _pg_enum(ActionState, "action_state"), default=ActionState.RECOMMENDED
    )
    request_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    result_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    case: Mapped["Case"] = relationship(back_populates="action_executions")
    approvals: Mapped[list["Approval"]] = relationship(
        back_populates="action_execution", cascade="all, delete-orphan"
    )


class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    approval_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), index=True
    )
    action_execution_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("action_executions.id", ondelete="SET NULL"), nullable=True
    )
    route: Mapped[ApprovalRoute] = mapped_column(
        _pg_enum(ApprovalRoute, "approval_route")
    )
    decided_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str] = mapped_column(Text, default="")

    action_execution: Mapped["ActionExecution | None"] = relationship(
        back_populates="approvals"
    )


class SarReport(Base, TimestampMixin):
    __tablename__ = "sar_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cases.case_id", ondelete="CASCADE"), unique=True
    )
    file: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str] = mapped_column(Text, default="")
    narrative: Mapped[str] = mapped_column(Text, default="")
    subjects: Mapped[list[str]] = mapped_column(JSONB, default=list)
    total_amount_usd: Mapped[float] = mapped_column(Float, default=0.0)
    activity_dates: Mapped[list[str]] = mapped_column(JSONB, default=list)

    case: Mapped["Case"] = relationship(back_populates="sar_report")


class PolicyRule(Base, TimestampMixin):
    __tablename__ = "policy_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(16), index=True)
    version: Mapped[str] = mapped_column(String(16), default="1.0")
    description: Mapped[str] = mapped_column(Text, default="")
    conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    route: Mapped[ApprovalRoute | None] = mapped_column(
        _pg_enum(ApprovalRoute, "approval_route"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)
