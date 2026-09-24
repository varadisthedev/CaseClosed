from datetime import datetime
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    ActionPhase,
    ActionState,
    ActionType,
    ApprovalRoute,
    CaseStatus,
    Pattern,
    Verdict,
)
from app.core.policy_rules import DEFAULT_POLICY_RULES, POLICY_VERSION
from app.db.models import ActionExecution, AuditEvent, PolicyRule
from app.repositories.action_repository import ActionRepository
from app.db.session import get_session_factory
from app.schemas.action import (
    ActionRecommendation,
    ApprovalRead,
    PolicyDecision,
    SARContent,
    SARSubject,
)
from app.services.as_of import AsOfError, epoch_utc
from app.services.evidence_service import new_event_id, new_approval_id


class PolicyViolationError(ValueError):
    """An action cannot be authorized under the current policy version."""


def _epoch(value: datetime | None) -> float:
    if value is None:
        return 0.0
    return epoch_utc(value)


class PolicyService:
    """Deterministic policy engine (AGENTS.md section 18).

    The LLM proposes; this service alone may authorize. Decisions are
    deterministic, versioned and recorded for audit. State machine:

        RECOMMENDED -> HUMAN_APPROVAL_REQUIRED -> AUTHORIZED -> EXECUTABLE

    Route L1 requires one human approval; L2 requires two.
    """

    source = "policy"
    version = POLICY_VERSION

    def __init__(self, session: Session | None = None) -> None:
        self.session = session or get_session_factory()()
        self._rules: list[PolicyRule] = []
        self._restart()

    def _restart(self, session: Session | None = None) -> None:
        self.session = session or get_session_factory()()
        self.repo = ActionRepository(self.session)
        self._seed_default_rules()
        self._load_rules()

    def _seed_default_rules(self) -> None:
        """Ensure default policy rules exist in the database."""
        existing = self.session.scalar(select(PolicyRule).limit(1))
        if existing:
            return
        for rule_data in DEFAULT_POLICY_RULES:
            rule = PolicyRule(
                rule_id=rule_data["rule_id"],
                description=rule_data["description"],
                conditions=rule_data["conditions"],
                action=rule_data["action"],
                route=rule_data.get("route"),
                approval_required=rule_data.get("approval_required", False),
                version=POLICY_VERSION,
                active=True,
            )
            self.session.add(rule)
        self.session.commit()

    def _load_rules(self) -> None:
        stmt = (
            select(PolicyRule)
            .where(PolicyRule.active.is_(True))
            .order_by(PolicyRule.created_at.asc())
        )
        self._rules = list(self.session.scalars(stmt).all())

    # --- rule matching -------------------------------------------------------

    def evaluate(
        self,
        *,
        case_id: str,
        phase: ActionPhase,
        recommendation: ActionRecommendation,
        verdict: Verdict,
        fraud_probability: float | None,
        pattern: Pattern | None,
        exposure_usd: float | None = None,
        input_risk_score: float | None = None,
        connected_cards: int = 0,
        as_of: datetime | None = None,
        recommendations_seen: int = 1,
    ) -> PolicyDecision:
        """Evaluate a proposed action against all active policy rules.

        Deterministic, no LLM. Every matched rule is recorded for audit.
        """
        evidence = (
            self.session.scalar(
                select(AuditEvent).where(AuditEvent.case_id == case_id).limit(1)
            )
            is not None
        )

        matched: list[str] = []
        action = recommendation.action
        route: ApprovalRoute | None = None
        approval_required = False

        def _route_priority(r: ApprovalRoute) -> int:
            return {"L2": 3, "L1": 2, "AUTO": 1}.get(r.value, 0)

        for rule in self._rules:
            if not self._rule_applies(
                rule,
                phase=phase,
                action=action,
                verdict=verdict,
                fraud_probability=fraud_probability,
                pattern=pattern,
                exposure_usd=exposure_usd,
                input_risk_score=input_risk_score,
                connected_cards=connected_cards,
                as_of=as_of,
            ):
                continue
            matched.append(rule.rule_id)
            if rule.route is not None:
                if route is None or _route_priority(rule.route) > _route_priority(route):
                    route = rule.route
            if rule.approval_required:
                approval_required = True
            # action override not implemented in current schema; use original action
            # action = rule.action_override or action

        state, detail = self._state_for(
            action=action,
            approval_required=approval_required,
            route=route,
            matched=matched,
        )

        decision = PolicyDecision(
            request_id=recommendation.request_id,
            action=action,
            state=state,
            approval_required=approval_required,
            approval_route=route,
            matched_rules=matched,
            policy_version=self.version,
            decision_detail=detail,
        )
        self._audit_decision(case_id, decision)
        return decision

    def _rule_applies(
        self,
        rule: PolicyRule,
        *,
        phase: ActionPhase,
        action: ActionType,
        verdict: Verdict,
        fraud_probability: float | None,
        pattern: Pattern | None,
        exposure_usd: float | None,
        input_risk_score: float | None,
        connected_cards: int,
        as_of: datetime | None,
    ) -> bool:
        if rule.conditions is None:
            return True
        conds = rule.conditions
        if "action_types" in conds and action.value not in conds["action_types"]:
            return False
        if "after_phase" in conds:
            raise ValueError(
                "PLACEHOLDER(policy-ghost-condition): rule uses an unresolved "
                "spatial qualifier (AGENTS.md does not define after-phase); "
                "rewrite the rule"
            )
        risk_score = input_risk_score
        for key, expected in conds.items():
            if key.startswith("fraud_probability"):
                value = fraud_probability
                if value is None:
                    return False
                if key == "fraud_probability_min":
                    if value < float(expected):
                        return False
                elif key == "fraud_probability_max":
                    if value > float(expected):
                        return False
                continue
            if key.startswith("verdict"):
                if verdict != Verdict(expected):
                    return False
                continue
            if key == "pattern_any":
                if pattern is None or pattern.value not in expected:
                    return False
                continue
            if key == "pattern_eq":
                if pattern is None or pattern != Pattern(expected):
                    return False
                continue
            if key == "pattern_none":
                if pattern is not None and pattern != Pattern.NONE:
                    return False
                continue
            if key.startswith("exposure"):
                if exposure_usd is None or exposure_usd < float(expected):
                    return False
                continue
            if key == "input_risk_score_min":
                if risk_score is None or risk_score < float(expected):
                    return False
                continue
            if key == "risk_score_max":
                if risk_score is None or risk_score > float(expected):
                    return False
                continue
            if key == "evidence_count":
                # Evidence count would require additional context - skip for now
                # PLACEHOLDER(policy-evidence-count): implement evidence count check
                continue
            # unknown key: refuse silently-silent policy drift
            raise ValueError(
                f"PLACEHOLDER(policy-unknown-condition): policy rule {rule.rule_id} "
                f"uses condition {key!r} that the engine does not understand"
            )
        return True

    def _state_for(
        self,
        *,
        action: ActionType,
        approval_required: bool,
        route: ApprovalRoute | None,
        matched: list[str],
    ) -> tuple[ActionState, str]:
        if approval_required or route in (ApprovalRoute.L1, ApprovalRoute.L2):
            if route == ApprovalRoute.L2:
                return (
                    ActionState.HUMAN_APPROVAL_REQUIRED,
                    f"L2 approval required (two approvers); rules {matched}",
                )
            if route == ApprovalRoute.L1:
                return (
                    ActionState.HUMAN_APPROVAL_REQUIRED,
                    f"L1 approval required; rules {matched}",
                )
            return (
                ActionState.HUMAN_APPROVAL_REQUIRED,
                f"approval required; rules {matched}",
            )
        return (
            ActionState.AUTHORIZED,
            f"no approval required; rules {matched}",
        )

    def _audit_decision(self, case_id: str, decision: PolicyDecision) -> None:
        self.repo.log_audit(
            event_id=new_event_id(),
            event_type="policy.decision",
            case_id=case_id,
            policy_version=decision.policy_version,
            matched_rule_ids=decision.matched_rules,
            actor="policy_engine",
            detail={
                "action": decision.action.value,
                "state": decision.state.value,
                "approval_route": decision.approval_route.value
                if decision.approval_route
                else None,
                "approval_required": decision.approval_required,
            },
        )
        self.session.commit()

    # --- approvals -----------------------------------------------------------

    def request_approval(
        self,
        *,
        case_id: str,
        decision: PolicyDecision,
        decided_by: str | None = None,
        notes: str = "",
    ) -> ApprovalRead:
        if not decision.approval_required or decision.approval_route is None:
            raise PolicyViolationError(
                f"action {decision.action.value} does not require approval"
            )
        approval = self.repo.create_approval(
            approval_id=new_approval_id(case_id),
            case_id=case_id,
            route=decision.approval_route,
            decision=decision.action.value,
            notes=notes,
        )
        self.session.commit()
        return ApprovalRead.model_validate(approval)

    def execute(
        self,
        *,
        case_id: str,
        decision: PolicyDecision,
        as_of: datetime | None = None,
    ) -> ActionExecution:
        if decision.state == ActionState.HUMAN_APPROVAL_REQUIRED:
            raise PolicyViolationError(
                f"action {decision.action.value} still needs approval"
            )
        execution = self.repo.create_execution(
            execution_id=f"EX-{case_id}-{new_event_id()}",
            idempotency_key=f"idem-{case_id}-{decision.action.value}",
            case_id=case_id,
            action=decision.action.value,
            route=decision.approval_route or ApprovalRoute.AUTO,
            state=ActionState.EXECUTABLE,
            request_payload={"decision": decision.model_dump()},
        )
        self.session.commit()
        return execution

    def approve_escalation(self, case_id: str, approver: str, notes: str = "") -> ApprovalRead:
        raise NotImplementedError(
            "PLACEHOLDER(policy-approval-wf): approval workflow endpoint not "
            "implemented yet; see PLACEHOLDERS.md"
        )