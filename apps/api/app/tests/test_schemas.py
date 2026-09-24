from datetime import datetime

from pydantic import ValidationError
import pytest

from app.schemas.case import CaseCreate, CaseRead
from app.schemas.evidence import EvidenceRead
from app.schemas.risk import RiskAssessment, RiskFactor
from app.core.enums import TriggerType


def test_case_create_allows_attributes_bag() -> None:
    case = CaseCreate(
        trigger_type=TriggerType.RISK_SCORE,
        trigger_text="over threshold",
        flagged_txn_id="T1",
        card_id="C1",
        customer_id="CU1",
        attributes={"TransactionAmt": 129.0, "ProductCD": "W"},
    )
    assert case.attributes["TransactionAmt"] == 129.0


def test_case_create_requires_flagged_txn() -> None:
    with pytest.raises(ValidationError):
        CaseCreate(
            trigger_type=TriggerType.RISK_SCORE,
            card_id="C1",
            customer_id="CU1",
        )


def test_case_read_deserializes_from_orm() -> None:
    data = {
        "case_id": "HHG-001",
        "trigger_type": "risk_score",
        "trigger_text": "",
        "flagged_txn_id": "T1",
        "card_id": "C1",
        "customer_id": "CU1",
        "opened_at": "2024-01-01T00:00:00Z",
        "pattern": "none",
    }
    read = CaseRead.model_validate(data)
    assert read.pattern == "none"


def test_evidence_read_defaults() -> None:
    ev = EvidenceRead.model_validate(
        {
            "evidence_id": "EV-1",
            "case_id": "HHG-001",
            "type": "graph",
            "claim": "c",
        }
    )
    assert ev.provisional is True
    assert ev.entity_ids == []
    assert ev.source == "placeholder"
    assert ev.confidence is None


def test_risk_assessment_has_factors_and_calibration_flag() -> None:
    risk = RiskAssessment(
        transaction_id="T1",
        score=0.42,
        band="MEDIUM",
        top_factors=[
            RiskFactor(factor="velocity", value=12, contribution=0.1, direction="up")
        ],
        model_version="xgb-v1",
    )
    assert risk.calibrated is False  # not claiming calibration without proof
    assert risk.top_factors[0].factor == "velocity"