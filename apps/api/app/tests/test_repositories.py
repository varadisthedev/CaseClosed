from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.core.enums import (
    ActionPhase,
    ActionState,
    ActionType,
    ApprovalRoute,
    EvidenceRequestType,
    RunStatus,
    TriggerType,
)
from app.db.session import get_session_factory, init_db
from app.repositories import (
    ActionRepository,
    CaseRepository,
    EvidenceRepository,
    RunRepository,
)
from app.schemas.case import CaseCreate


@pytest.fixture()
def session() -> Session:
    init_db()
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def test_case_repository_roundtrip(session: Session) -> None:
    repo = CaseRepository(session)
    case = repo.create(
        CaseCreate(
            case_id="HHG-900",
            trigger_type=TriggerType.RISK_SCORE,
            trigger_text="Risk over threshold",
            flagged_txn_id="T1",
            card_id="C1",
            customer_id="CUST1",
            input_risk_score=0.85,
            opened_at=datetime(2024, 1, 1),
        )
    )
    repo.add_transaction("HHG-900", "T1", is_flagged=True, amount_usd=100.0)
    repo.add_transaction("HHG-900", "T2", amount_usd=200.0)
    repo.add_connected_card("HHG-900", "C2", reason="shared device")
    repo.add_connected_device("HHG-900", "dev-1", reason="same device")
    repo.add_similar_case("HHG-900", "HHG-001", similarity=0.8, rank=1)
    session.commit()

    fetched = repo.get("HHG-900")
    assert fetched is not None
    assert fetched.input_risk_score == 0.85
    assert len(repo.transactions("HHG-900")) == 2
    assert len(repo.connected_cards("HHG-900")) == 1
    assert len(repo.connected_devices("HHG-900")) == 1
    assert len(repo.similar_cases("HHG-900")) == 1


def test_evidence_repository_roundtrip(session: Session) -> None:
    CaseRepository(session).create(
        CaseCreate(
            case_id="HHG-901",
            trigger_type=TriggerType.CUSTOMER_REPORT,
            trigger_text="Customer report",
            flagged_txn_id="T3",
            card_id="C1",
            customer_id="CUST1",
        )
    )
    ev = EvidenceRepository(session)
    ev.create(
        evidence_id="EV-1",
        case_id="HHG-901",
        claim="txn T3 shares device with C2",
        type="graph",
        source="graph",
        source_ref="query:shared_device",
        confidence=0.92,
        entity_ids=["C2", "dev-1"],
    )
    req = ev.create_request(
        request_id="RQ-1",
        case_id="HHG-901",
        type=EvidenceRequestType.CUSTOMER_VALIDATION,
        assumed_response="20191101 order",
    )
    session.commit()

    assert ev.get("EV-1").claim.startswith("txn T3")
    assert len(ev.get_for_case("HHG-901")) == 1
    assert ev.get_request("RQ-1").status.value == "pending"


def test_action_repository_roundtrip(session: Session) -> None:
    CaseRepository(session).create(
        CaseCreate(
            case_id="HHG-902",
            trigger_type=TriggerType.ANALYST_REQUEST,
            trigger_text="Analyst requested review",
            flagged_txn_id="T4",
            card_id="C1",
            customer_id="CUST1",
        )
    )
    ar = ActionRepository(session)
    ar.create_next_best(
        case_id="HHG-902",
        phase=ActionPhase.FINAL,
        action=ActionType.BLOCK_CARD,
        route=ApprovalRoute.L1,
        reason="high risk shared device",
        policy_rule="R-P1",
        order_index=0,
    )
    ar.create_execution(
        execution_id="EX-1",
        idempotency_key="idem-1",
        case_id="HHG-902",
        action=ActionType.BLOCK_CARD,
        route=ApprovalRoute.L1,
        state=ActionState.EXECUTED,
    )
    ar.create_approval(
        approval_id="AP-1",
        case_id="HHG-902",
        route=ApprovalRoute.L1,
        decided_by="analyst",
        decision="APPROVED",
    )
    ar.upsert_sar_report(case_id="HHG-902", file=True, reason="SAR needed")
    ar.log_audit(
        event_id="AU-1",
        event_type="policy.decision",
        case_id="HHG-902",
        policy_version="1.0",
        matched_rule_ids=["R-P1"],
    )
    session.commit()

    assert len(ar.list_next_best("HHG-902")) == 1
    assert ar.get_execution("EX-1").state == ActionState.EXECUTED
    assert ar.get_execution_by_idempotency_key("idem-1").execution_id == "EX-1"
    assert len(ar.list_approvals("HHG-902")) == 1
    assert ar.get_sar_report("HHG-902").file is True
    assert len(ar.list_audit_events("HHG-902")) == 1


def test_run_repository_roundtrip(session: Session) -> None:
    rr = RunRepository(session)
    run = rr.create_run(run_id="RUN-1", case_id="HHG-900")
    rr.add_step("RUN-1", 0, "investigate_graph", {"query": "shared_device"})
    rr.add_step("RUN-1", 1, "assess_risk", {"score": 0.8})
    rr.update_run("RUN-1", status=RunStatus.COMPLETED)
    session.commit()

    assert rr.get_run("RUN-1").status == RunStatus.COMPLETED
    assert len(rr.list_steps("RUN-1")) == 2
    assert rr.list_steps("RUN-1")[1].node_name == "assess_risk"