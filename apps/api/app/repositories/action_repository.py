from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ActionPhase, ActionState, ApprovalRoute
from app.db.models import (
    ActionExecution,
    Approval,
    AuditEvent,
    NextBestAction,
    PolicyRule,
    SarReport,
)


class ActionRepository:
    """Persistence for actions, approvals, policy rules and audit events."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- NextBestAction ------------------------------------------------------
    def create_next_best(
        self,
        *,
        case_id: str,
        phase: ActionPhase,
        action: str,
        route: ApprovalRoute,
        reason: str = "",
        policy_rule: str = "",
        order_index: int = 0,
    ) -> NextBestAction:
        record = NextBestAction(
            case_id=case_id,
            phase=phase,
            action=action,
            route=route,
            reason=reason,
            policy_rule=policy_rule,
            order_index=order_index,
        )
        self.session.add(record)
        return record

    def list_next_best(self, case_id: str) -> list[NextBestAction]:
        stmt = (
            select(NextBestAction)
            .where(NextBestAction.case_id == case_id)
            .order_by(NextBestAction.order_index)
        )
        return list(self.session.scalars(stmt).all())

    def clear_next_best(self, case_id: str) -> None:
        self.session.query(NextBestAction).filter_by(case_id=case_id).delete()

    # --- ActionExecution -----------------------------------------------------
    def create_execution(
        self,
        *,
        execution_id: str,
        idempotency_key: str,
        case_id: str,
        action: str,
        route: ApprovalRoute = ApprovalRoute.L1,
        state: ActionState = ActionState.RECOMMENDED,
        request_payload: dict[str, Any] | None = None,
        result_payload: dict[str, Any] | None = None,
    ) -> ActionExecution:
        record = ActionExecution(
            execution_id=execution_id,
            idempotency_key=idempotency_key,
            case_id=case_id,
            action=action,
            route=route,
            state=state,
            request_payload=request_payload or {},
            result_payload=result_payload or {},
        )
        self.session.add(record)
        return record

    def get_execution(self, execution_id: str) -> ActionExecution | None:
        return self.session.scalar(
            select(ActionExecution).where(ActionExecution.execution_id == execution_id)
        )

    def get_execution_by_idempotency_key(self, key: str) -> ActionExecution | None:
        stmt = select(ActionExecution).where(ActionExecution.idempotency_key == key)
        return self.session.scalar(stmt)

    def update_execution(self, execution_id: str, **values: Any) -> ActionExecution | None:
        record = self.get_execution(execution_id)
        if record is None:
            return None
        for key, value in values.items():
            if hasattr(record, key):
                setattr(record, key, value)
        return record

    def list_executions(self, case_id: str) -> list[ActionExecution]:
        stmt = select(ActionExecution).where(ActionExecution.case_id == case_id)
        return list(self.session.scalars(stmt).all())

    # --- Approval ------------------------------------------------------------
    def create_approval(
        self,
        *,
        approval_id: str,
        case_id: str,
        route: ApprovalRoute,
        action_execution_id: int | None = None,
        decided_by: str | None = None,
        decision: str | None = None,
        decided_at: datetime | None = None,
        notes: str = "",
    ) -> Approval:
        record = Approval(
            approval_id=approval_id,
            case_id=case_id,
            route=route,
            action_execution_id=action_execution_id,
            decided_by=decided_by,
            decision=decision,
            decided_at=decided_at,
            notes=notes,
        )
        self.session.add(record)
        return record

    def get_approval(self, approval_id: str) -> Approval | None:
        return self.session.scalar(
            select(Approval).where(Approval.approval_id == approval_id)
        )

    def update_approval(self, approval_id: str, **values: Any) -> Approval | None:
        record = self.get_approval(approval_id)
        if record is None:
            return None
        for key, value in values.items():
            if hasattr(record, key):
                setattr(record, key, value)
        return record

    def list_approvals(self, case_id: str) -> list[Approval]:
        stmt = select(Approval).where(Approval.case_id == case_id)
        return list(self.session.scalars(stmt).all())

    # --- SarReport -----------------------------------------------------------
    def get_sar_report(self, case_id: str) -> SarReport | None:
        stmt = select(SarReport).where(SarReport.case_id == case_id)
        return self.session.scalar(stmt)

    def upsert_sar_report(self, case_id: str, **values: Any) -> SarReport:
        report = self.get_sar_report(case_id)
        if report is None:
            report = SarReport(case_id=case_id, **values)
            self.session.add(report)
        else:
            for key, value in values.items():
                if hasattr(report, key):
                    setattr(report, key, value)
        return report

    # --- PolicyRule ----------------------------------------------------------
    def upsert_policy_rule(self, rule: dict[str, Any]) -> PolicyRule:
        record = self.session.scalar(
            select(PolicyRule).where(PolicyRule.rule_id == rule["rule_id"])
        )
        if record is None:
            record = PolicyRule(**rule)
            self.session.add(record)
        else:
            for key, value in rule.items():
                if hasattr(record, key):
                    setattr(record, key, value)
        return record

    def list_policy_rules(self, active_only: bool = True) -> list[PolicyRule]:
        stmt = select(PolicyRule).order_by(PolicyRule.rule_id)
        if active_only:
            stmt = stmt.where(PolicyRule.active.is_(True))
        return list(self.session.scalars(stmt).all())

    def get_policy_version(self) -> str:
        rule = self.session.scalar(
            select(PolicyRule).order_by(PolicyRule.created_at.desc())
        )
        return rule.version if rule else "1.0"

    # --- AuditEvent ----------------------------------------------------------
    def log_audit(
        self,
        *,
        event_id: str,
        event_type: str,
        case_id: str | None = None,
        policy_version: str | None = None,
        matched_rule_ids: list[str] | None = None,
        actor: str = "agent",
        detail: dict[str, Any] | None = None,
    ) -> AuditEvent:
        record = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            case_id=case_id,
            policy_version=policy_version,
            matched_rule_ids=matched_rule_ids or [],
            actor=actor,
            detail=detail or {},
        )
        self.session.add(record)
        return record

    def list_audit_events(self, case_id: str | None = None, limit: int = 100) -> list[AuditEvent]:
        stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
        if case_id:
            stmt = select(AuditEvent).where(AuditEvent.case_id == case_id)
            stmt = stmt.order_by(AuditEvent.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())