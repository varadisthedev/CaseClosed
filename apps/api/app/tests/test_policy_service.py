from datetime import datetime, timezone

import pytest

from app.core.enums import (
    ActionPhase,
    ActionState,
    ActionType,
    ApprovalRoute,
    Pattern,
    Verdict,
)
from app.core.policy_rules import DEFAULT_POLICY_RULES, POLICY_VERSION
from app.db.session import init_db
from app.schemas.action import ActionRecommendation
from app.services.policy_service import PolicyService, PolicyViolationError

CASE = "HHG-P1"
P1 = datetime(2024, 2, 1, tzinfo=timezone.utc)


def _recommendation(
    action: ActionType,
    *,
    route: ApprovalRoute | None = None,
) -> ActionRecommendation:
    return ActionRecommendation(
        request_id=f"AR-{action.value}",
        phase=ActionPhase.INITIAL,
        action=action,
        route=route or ApprovalRoute.AUTO,
        reason="Test recommendation",
        policy_rule="",
    )


@pytest.fixture(scope="function")
def svc() -> PolicyService:
    init_db()
    session = None
    return PolicyService()


def test_policy_version_is_stable_and_rules_are_seeded(svc: PolicyService) -> None:
    rules = svc._rules
    assert rules  # seeded from DEFAULT_POLICY_RULES
    assert {r.rule_id for r in rules} == {r["rule_id"] for r in DEFAULT_POLICY_RULES}
    assert svc.version == POLICY_VERSION


def test_high_risk_step_up_requires_l1_approval(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.INITIAL,
        recommendation=_recommendation(ActionType.STEP_UP_AUTH),
        verdict=Verdict.FRAUD,
        fraud_probability=0.9,
        pattern=Pattern.CARD_NOT_PRESENT_NEW_DEVICE,
        exposure_usd=2000.0,
        input_risk_score=None,
        connected_cards=0,
    )
    assert decision.approval_required is True
    assert decision.approval_route == ApprovalRoute.L2
    assert decision.state == ActionState.HUMAN_APPROVAL_REQUIRED
    assert "R-2" in decision.matched_rules


def test_account_takeover_requires_l2_approval(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.INITIAL,
        recommendation=_recommendation(ActionType.BLOCK_CARD),
        verdict=Verdict.FRAUD,
        fraud_probability=0.95,
        pattern=Pattern.ACCOUNT_TAKEOVER,
        exposure_usd=5000.0,
        input_risk_score=0.8,
        connected_cards=1,
    )
    assert decision.approval_required is True
    assert decision.approval_route == ApprovalRoute.L2
    assert decision.state == ActionState.HUMAN_APPROVAL_REQUIRED
    assert "R-3" in decision.matched_rules


def test_low_risk_no_approval(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.FINAL,
        recommendation=_recommendation(ActionType.CLOSE_NO_FRAUD),
        verdict=Verdict.LEGITIMATE,
        fraud_probability=0.1,
        pattern=Pattern.NONE,
        exposure_usd=100.0,
        input_risk_score=0.2,
        connected_cards=0,
    )
    assert decision.approval_required is False
    assert decision.state == ActionState.AUTHORIZED
    assert "R-4" in decision.matched_rules


def test_sar_filing_requires_l2(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.FINAL,
        recommendation=_recommendation(ActionType.FILE_REPORT),
        verdict=Verdict.FRAUD,
        fraud_probability=0.8,
        pattern=Pattern.CARD_NOT_PRESENT_NEW_DEVICE,
        exposure_usd=15000.0,
        input_risk_score=0.7,
        connected_cards=2,
    )
    assert decision.approval_required is True
    assert decision.approval_route == ApprovalRoute.L2
    assert decision.state == ActionState.HUMAN_APPROVAL_REQUIRED
    assert "R-5" in decision.matched_rules


def test_gather_evidence_when_no_evidence(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.INITIAL,
        recommendation=_recommendation(ActionType.MONITOR_CARD),
        verdict=Verdict.UNCERTAIN,
        fraud_probability=0.5,
        pattern=None,
        exposure_usd=None,
        input_risk_score=None,
        connected_cards=0,
    )
    assert decision.approval_required is False
    assert decision.state == ActionState.AUTHORIZED
    assert "R-6" in decision.matched_rules


def test_request_approval_creates_approval(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.INITIAL,
        recommendation=_recommendation(ActionType.STEP_UP_AUTH),
        verdict=Verdict.FRAUD,
        fraud_probability=0.9,
        pattern=Pattern.CARD_NOT_PRESENT_NEW_DEVICE,
        exposure_usd=2000.0,
        input_risk_score=None,
        connected_cards=0,
    )
    approval = svc.request_approval(case_id=CASE, decision=decision)
    assert approval.approval_id.startswith("AP-")
    assert approval.route == ApprovalRoute.L2
    assert approval.case_id == CASE


def test_execute_unapproved_raises(svc: PolicyService) -> None:
    decision = svc.evaluate(
        case_id=CASE,
        phase=ActionPhase.INITIAL,
        recommendation=_recommendation(ActionType.STEP_UP_AUTH),
        verdict=Verdict.FRAUD,
        fraud_probability=0.9,
        pattern=Pattern.CARD_NOT_PRESENT_NEW_DEVICE,
        exposure_usd=2000.0,
        input_risk_score=None,
        connected_cards=0,
    )
    with pytest.raises(PolicyViolationError):
        svc.execute(case_id=CASE, decision=decision)