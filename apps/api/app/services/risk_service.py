from datetime import datetime, timezone
from typing import Any

from app.core.enums import Verdict, Pattern
from app.db.session import get_session_factory, init_db
from app.services.evidence_service import EvidenceService, new_evidence_id


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def assess_risk(
    case_id: str,
    *,
    input_risk_score: float | None = None,
    fraud_probability: float | None = None,
    pattern: Pattern | None = None,
    exposure_usd: float | None = None,
    connected_cards: int = 0,
) -> dict:
    """Assess risk for a case based on evidence and patterns.

    Returns a risk assessment with score, band, top factors, and verdict.
    Deterministic: no LLM calls, purely rule-based assessment.
    """
    init_db()
    svc = EvidenceService()

    # Build risk factors from provided data
    factors: list[str] = []
    risk_score = input_risk_score
    verdict = Verdict.UNCERTAIN

    if fraud_probability is not None:
        factors.append(f"fraud_probability={fraud_probability:.2f}")
        if fraud_probability >= 0.7:
            verdict = Verdict.FRAUD
        elif fraud_probability >= 0.4:
            verdict = Verdict.UNCERTAIN
        else:
            verdict = Verdict.LEGITIMATE

    if pattern is not None:
        factors.append(f"pattern={pattern.value}")
        if pattern.value == "account_takeover":
            verdict = Verdict.FRAUD
        elif pattern.value == "card_not_present":
            if fraud_probability is not None and fraud_probability > 0.5:
                verdict = Verdict.FRAUD
            else:
                verdict = Verdict.UNCERTAIN

    if exposure_usd is not None:
        factors.append(f"exposure_usd={exposure_usd:.2f}")
        if exposure_usd >= 10000:
            verdict = Verdict.FRAUD
        elif exposure_usd >= 1000:
            if verdict != Verdict.FRAUD:
                verdict = Verdict.UNCERTAIN

    if input_risk_score is not None:
        factors.append(f"input_risk_score={input_risk_score:.2f}")
        if input_risk_score >= 0.7:
            verdict = Verdict.FRAUD
        elif input_risk_score >= 0.4:
            if verdict != Verdict.FRAUD:
                verdict = Verdict.UNCERTAIN

    if connected_cards > 1:
        factors.append(f"connected_cards={connected_cards}")
        if verdict != Verdict.FRAUD:
            verdict = Verdict.UNCERTAIN

    # Determine band based on risk level
    if verdict == Verdict.FRAUD:
        band = "high"
        top_factors = factors[:3] if len(factors) >= 3 else factors
    elif verdict == Verdict.UNCERTAIN:
        band = "medium"
        top_factors = factors[:2] if len(factors) >= 2 else factors
    else:
        band = "low"
        top_factors = factors[:2] if len(factors) >= 2 else factors

    # If no factors provided, return default low risk
    if not factors:
        return {
            "score": 0.0,
            "band": "low",
            "top_factors": [],
            "verdict": "legitimate",
            "calibrated": False,
            "model_version": "stub",
            "source": "risk_service.stub",
        }

    return {
        "score": float(fraud_probability) if fraud_probability is not None else (
            0.8 if verdict == Verdict.FRAUD else 0.3
        ),
        "band": band,
        "top_factors": top_factors,
        "verdict": verdict.value,
        "calibrated": False,
        "model_version": "stub",
        "source": "risk_service.stub",
    }


def get_risk_factors(
    case_id: str,
    *,
    input_risk_score: float | None = None,
    fraud_probability: float | None = None,
    pattern: Pattern | None = None,
) -> dict:
    """Get risk factors for a case without assigning a verdict.

    Used by the investigation service to gather evidence-based risk information.
    """
    init_db()
    factors: list[str] = []

    if input_risk_score is not None:
        factors.append(f"input_risk_score={input_risk_score:.2f}")

    if fraud_probability is not None:
        factors.append(f"fraud_probability={fraud_probability:.2f}")

    if pattern is not None:
        factors.append(f"pattern={pattern.value}")

    return {
        "case_id": case_id,
        "risk_factors": factors,
        "source": "risk_service.stub",
    }


def investigate_case(
    case_id: str,
    *,
    input_risk_score: float | None = None,
    fraud_probability: float | None = None,
    pattern: Pattern | None = None,
    exposure_usd: float | None = None,
    connected_cards: int = 0,
) -> dict:
    """Run a full risk investigation for a case.

    Combines risk assessment with evidence gathering to produce a
    complete investigation snapshot.
    """
    init_db()
    evidence_svc = EvidenceService()

    # Get risk assessment
    risk = assess_risk(
        case_id=case_id,
        input_risk_score=input_risk_score,
        fraud_probability=fraud_probability,
        pattern=pattern,
        exposure_usd=exposure_usd,
        connected_cards=connected_cards,
    )

    # Gather evidence factors
    factors = get_risk_factors(
        case_id=case_id,
        input_risk_score=input_risk_score,
        fraud_probability=fraud_probability,
        pattern=pattern,
    )

    return {
        "case_id": case_id,
        "risk_assessment": risk,
        "risk_factors": factors["risk_factors"],
        "investigation_timestamp": _now_utc().isoformat(),
        "source": "risk_service.stub",
    }