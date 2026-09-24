from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import CaseStatus, Pattern, TriggerType, Verdict


class CaseCreate(BaseModel):
    """Intake for a new case.

    Only stable IDs and timestamps are required. Any dataset-specific fields
    belong in ``attributes`` (AGENTS.md section 4: do not invent column
    meanings).
    """

    case_id: str | None = None
    trigger_type: TriggerType
    trigger_text: str = ""
    flagged_txn_id: str
    card_id: str
    customer_id: str
    input_risk_score: float | None = None
    opened_at: datetime | None = None
    as_of: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class CaseUpdate(BaseModel):
    status: CaseStatus | None = None
    verdict: Verdict | None = None
    fraud_probability: float | None = None
    pattern: Pattern | None = None
    pattern_description: str | None = None
    first_suspicious_txn_id: str | None = None
    exposure_usd: float | None = None
    summary: str | None = None
    written_to_graph: bool | None = None
    graph_case_id: str | None = None
    run_id: str | None = None


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    trigger_type: TriggerType
    trigger_text: str = ""
    flagged_txn_id: str
    card_id: str
    customer_id: str
    input_risk_score: float | None = None
    opened_at: datetime
    as_of: datetime | None = None
    status: CaseStatus | None = None
    verdict: Verdict | None = None
    fraud_probability: float | None = None
    pattern: Pattern | None = None
    pattern_description: str = ""
    first_suspicious_txn_id: str | None = None
    exposure_usd: float | None = None
    summary: str = ""
    written_to_graph: bool = False
    graph_case_id: str | None = None
    run_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None