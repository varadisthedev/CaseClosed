from datetime import datetime, timezone
from typing import Any

from app.core.enums import Verdict, Pattern
from app.db.session import get_session_factory, init_db
from app.services.policy_service import PolicyService, PolicyViolationError
from app.services.risk_service import assess_risk, investigate_case, get_risk_factors
from app.services.rag_service import build_grounded_context, validate_evidence_ids, retrieve_similar_cases, resolve_entities
from app.services.evidence_service import EvidenceService, new_evidence_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_investigation(
    case_id: str,
    *,
    as_of: datetime | None = None,
    include_pattern: Pattern | None = None,
    include_similar: bool = True,
    include_risk: bool = True,
) -> dict:
    """Run a complete investigation for a case.

    Coordinates the full investigation workflow:
    1. Policy engine evaluation
    2. Risk assessment
    3. Graph evidence retrieval
    4. Similar case lookup
    5. Grounded context building for LLM explanation
    6. Evidence validation

    Returns a complete investigation result with findings, evidence,
    risk assessment, and next-best-action recommendations.
    """
    init_db()

    # Step 1: Policy engine evaluation
    policy_svc = PolicyService()
    policy_result = _evaluate_policy(case_id, as_of=as_of)

    # Step 2: Risk assessment
    risk_result = investigate_case(
        case_id=case_id,
        as_of=as_of,
        include_pattern=include_pattern,
    ) if include_risk else {"risk_assessment": None, "risk_factors": []}

    # Step 3: Build grounded context for LLM
    context = build_grounded_context(
        case_id=case_id,
        as_of=as_of,
        include_pattern=include_pattern,
        include_similar=include_similar,
    )

    # Step 4: Validate evidence IDs in context
    # Collect all cited evidence IDs from the context and validate them
    cited_ids = []
    if context.get("evidence"):
        cited_ids = [e["evidence_id"] for e in context["evidence"]]
    validated_context = validate_evidence_ids(context, cited_ids)

    # Step 4: Retrieve similar cases
    similar_cases = retrieve_similar_cases(
        case_id=case_id,
        limit=5,
        as_of=as_of,
    ) if include_similar else []

    # Build the complete investigation result
    result = {
        "case_id": case_id,
        "policy": policy_result,
        "risk_assessment": risk_result.get("risk_assessment"),
        "risk_factors": risk_result.get("risk_factors", []),
        "grounded_context": validated_context,
        "similar_cases": similar_cases,
        "investigation_timestamp": _now_utc().isoformat(),
        "as_of": as_of.isoformat() if as_of else None,
        "source": "investigation_service.stub",
    }

    return result


def _evaluate_policy(case_id: str, *, as_of: datetime | None = None) -> dict:
    """Evaluate policy for a case using the policy service.

    Returns the policy decision with state, approval requirements,
    and matched rules.
    """
    init_db()
    policy_svc = PolicyService()

    # Create a recommendation based on case features
    # In a full implementation, this would use actual case data
    from app.schemas.action import ActionRecommendation
    from app.core.enums import ActionType, ActionPhase, ApprovalRoute

    rec = ActionRecommendation(
        request_id=f"INV-{case_id}",
        phase=ActionPhase.INITIAL,
        action=ActionType.STEP_UP_AUTH,
        route=ApprovalRoute.L1,
        reason="Policy evaluation for investigation",
        policy_rule="",
    )

    # Evaluate the policy - use conservative parameters
    decision = policy_svc.evaluate(
        case_id=case_id,
        phase=ActionPhase.INITIAL,
        recommendation=rec,
        verdict=Verdict.UNCERTAIN,
        fraud_probability=0.5,
        pattern=include_pattern,
        exposure_usd=None,
        input_risk_score=None,
        connected_cards=0,
        as_of=as_of,
    )

    return {
        "decision_state": decision.state.value,
        "approval_required": decision.approval_required,
        "approval_route": decision.approval_route.value if decision.approval_route else None,
        "matched_rules": decision.matched_rules,
        "policy_version": decision.policy_version,
        "decision_detail": decision.decision_detail,
    }


def check_approval_required(
    case_id: str,
    *,
    as_of: datetime | None = None,
) -> dict:
    """Check if a case requires approval and what the approval route is.

    Returns the approval status and route information.
    """
    init_db()
    policy_svc = PolicyService()

    from app.schemas.action import ActionRecommendation
    from app.core.enums import ActionType, ActionPhase, ApprovalRoute

    rec = ActionRecommendation(
        request_id=f"INV-{case_id}",
        phase=ActionPhase.INITIAL,
        action=ActionType.STEP_UP_AUTH,
        route=ApprovalRoute.L1,
        reason="Approval check for investigation",
        policy_rule="",
    )

    decision = policy_svc.evaluate(
        case_id=case_id,
        phase=ActionPhase.INITIAL,
        recommendation=rec,
        verdict=Verdict.UNCERTAIN,
        fraud_probability=0.5,
        pattern=None,
        exposure_usd=None,
        input_risk_score=None,
        connected_cards=0,
        as_of=as_of,
    )

    return {
        "approval_required": decision.approval_required,
        "approval_route": decision.approval_route.value if decision.approval_route else None,
        "state": decision.state.value,
        "policy_version": decision.policy_version,
    }