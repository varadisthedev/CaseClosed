from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.core.enums import ActionState, ActionType, ApprovalRoute
from app.db.models import ActionExecution, Approval, Case
from app.db.session import get_session_factory
from app.services.evidence_service import new_event_id, new_approval_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _generate_execution_id(case_id: str, action: str) -> str:
    import uuid
    return f"EX-{case_id}-{action}-{uuid.uuid4().hex[:8]}"


def _generate_idempotency_key(case_id: str, action: str) -> str:
    import uuid
    return f"IDEM-{case_id}-{action}-{uuid.uuid4().hex[:8]}"


def block_card(case_id: str, *, idempotency_key: str | None = None) -> dict:
    """Block the customer's card.

    Idempotent: same idempotency key returns same result.
    Persisted result recorded in ActionExecution.
    """
    idem_key = idempotency_key or _generate_idempotency_key(case_id, "block_card")
    execution_id = _generate_execution_id(case_id, "block_card")

    # Check for existing idempotent execution
    db = get_session_factory()()
    existing = db.scalar(
        select(ActionExecution).where(
            ActionExecution.idempotency_key == idem_key
        )
    )
    if existing:
        return {
            "execution_id": existing.execution_id,
            "case_id": case_id,
            "action": "block_card",
            "state": existing.state,
            "result": existing.result_payload or {},
            "executed_at": existing.executed_at,
        }

    execution = ActionExecution(
        execution_id=execution_id,
        idempotency_key=idem_key,
        case_id=case_id,
        action="block_card",
        route=ApprovalRoute.AUTO,
        state=ActionState.EXECUTABLE,
        request_payload={},
        result_payload={"card_blocked": True, "blocked_at": _now_utc().isoformat()},
        executed_at=_now_utc(),
    )
    db.add(execution)
    db.commit()
    db.close()

    return {
        "execution_id": execution_id,
        "case_id": case_id,
        "action": "block_card",
        "state": ActionState.EXECUTED.value,
        "result": {"card_blocked": True, "blocked_at": _now_utc().isoformat()},
        "executed_at": _now_utc().isoformat(),
    }


def step_up_authentication(case_id: str, *, idempotency_key: str | None = None) -> dict:
    """Step up authentication on the flagged card.

    Idempotent: same idempotency key returns same result.
    Persisted result recorded in ActionExecution.
    """
    idem_key = idempotency_key or _generate_idempotency_key(case_id, "step_up_authentication")
    execution_id = _generate_execution_id(case_id, "step_up_authentication")

    # Check for existing idempotent execution
    db = get_session_factory()()
    existing = db.scalar(
        select(ActionExecution).where(
            ActionExecution.idempotency_key == idem_key
        )
    )
    if existing:
        return {
            "execution_id": existing.execution_id,
            "case_id": case_id,
            "action": "step_up_authentication",
            "state": existing.state,
            "result": existing.result_payload or {},
            "executed_at": existing.executed_at,
        }

    execution = ActionExecution(
        execution_id=execution_id,
        idempotency_key=idem_key,
        case_id=case_id,
        action="step_up_authentication",
        route=ApprovalRoute.L2,
        state=ActionState.EXECUTABLE,
        request_payload={},
        result_payload={"step_up_initiated": True, "initiated_at": _now_utc().isoformat()},
        executed_at=_now_utc(),
    )
    db.add(execution)
    db.commit()
    db.close()

    return {
        "execution_id": execution_id,
        "case_id": case_id,
        "action": "step_up_authentication",
        "state": ActionState.EXECUTED.value,
        "result": {"step_up_initiated": True, "initiated_at": _now_utc().isoformat()},
        "executed_at": _now_utc().isoformat(),
    }


def contact_customer(case_id: str, *, idempotency_key: str | None = None, notes: str = "") -> dict:
    """Contact the customer regarding the investigation.

    Idempotent: same idempotency key returns same result.
    Persisted result recorded in ActionExecution.
    """
    idem_key = idempotency_key or _generate_idempotency_key(case_id, "contact_customer")
    execution_id = _generate_execution_id(case_id, "contact_customer")

    # Check for existing idempotent execution
    db = get_session_factory()()
    existing = db.scalar(
        select(ActionExecution).where(
            ActionExecution.idempotency_key == idem_key
        )
    )
    if existing:
        return {
            "execution_id": existing.execution_id,
            "case_id": case_id,
            "action": "contact_customer",
            "state": existing.state,
            "result": existing.result_payload or {},
            "executed_at": existing.executed_at,
        }

    execution = ActionExecution(
        execution_id=execution_id,
        idempotency_key=idem_key,
        case_id=case_id,
        action="contact_customer",
        route=ApprovalRoute.AUTO,
        state=ActionState.EXECUTABLE,
        request_payload={"notes": notes},
        result_payload={"customer_contacted": True, "contacted_at": _now_utc().isoformat(), "notes": notes},
        executed_at=_now_utc(),
    )
    db.add(execution)
    db.commit()
    db.close()

    return {
        "execution_id": execution_id,
        "case_id": case_id,
        "action": "contact_customer",
        "state": ActionState.EXECUTED.value,
        "result": {"customer_contacted": True, "contacted_at": _now_utc().isoformat(), "notes": notes},
        "executed_at": _now_utc().isoformat(),
    }


def file_sar(case_id: str, *, idempotency_key: str | None = None, sar_amount: float | None = None) -> dict:
    """File a Suspicious Activity Report.

    Idempotent: same idempotency key returns same result.
    Persisted result recorded in SarReport and ActionExecution.
    """
    idem_key = idempotency_key or _generate_idempotency_key(case_id, "file_sar")
    execution_id = _generate_execution_id(case_id, "file_sar")

    # Check for existing idempotent execution
    db = get_session_factory()()
    existing_execution = db.scalar(
        select(ActionExecution).where(
            ActionExecution.idempotency_key == idem_key
        )
    )
    if existing_execution:
        sar = db.scalar(select(SarReport).where(SarReport.case_id == case_id))
        return {
            "execution_id": existing_execution.execution_id,
            "case_id": case_id,
            "action": "file_sar",
            "state": existing_execution.state,
            "result": existing_execution.result_payload or {},
            "sar_report_id": sar.sar_report_id if sar else None,
            "executed_at": existing_execution.executed_at,
        }

    # Create SAR report
    from app.db.models import SarReport as SarReportModel
    sar = SarReportModel(
        case_id=case_id,
        sar_report_id=f"SAR-{case_id}-{uuid.uuid4().hex[:8]}",
        sar_amount=sar_amount or 0.0,
        filed_at=_now_utc(),
        status="filed",
        details={"idempotency_key": idem_key},
    )
    db.add(sar)

    execution = ActionExecution(
        execution_id=execution_id,
        idempotency_key=idem_key,
        case_id=case_id,
        action="file_sar",
        route=ApprovalRoute.L2,
        state=ActionState.EXECUTABLE,
        request_payload={"sar_amount": sar_amount},
        result_payload={"sar_filed": True, "sar_report_id": sar.sar_report_id, "sar_amount": sar_amount},
        executed_at=_now_utc(),
    )
    db.add(execution)
    db.commit()
    db.close()

    return {
        "execution_id": execution_id,
        "case_id": case_id,
        "action": "file_sar",
        "state": ActionState.EXECUTED.value,
        "result": {"sar_filed": True, "sar_report_id": sar.sar_report_id, "sar_amount": sar_amount},
        "executed_at": _now_utc().isoformat(),
        "sar_report_id": sar.sar_report_id,
    }


def create_case(case_id: str, *, idempotency_key: str | None = None, **kwargs: Any) -> dict:
    """Create a new investigation case.

    Idempotent: same idempotency key returns same result.
    Persisted result recorded in Case model.
    """
    idem_key = idempotency_key or _generate_idempotency_key(case_id, "create_case")

    # Check for existing idempotent creation
    from app.db.models import Case as CaseModel
    db = get_session_factory()()
    existing = db.scalar(select(CaseModel).where(CaseModel.case_id == case_id))
    if existing:
        return {
            "case_id": existing.case_id,
            "state": existing.state,
            "updated_at": existing.updated_at.isoformat() if existing.updated_at else None,
        }

    # Create new case (minimal fields)
    from datetime import datetime, timezone
    from sqlalchemy import func

    case = CaseModel(
        case_id=case_id,
        state="open",
        created_at=_now_utc(),
        updated_at=_now_utc(),
        **kwargs,
    )
    db.add(case)
    db.commit()
    db.close()

    return {
        "case_id": case_id,
        "state": "open",
        "created_at": _now_utc().isoformat(),
        "updated_at": _now_utc().isoformat(),
    }