from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import RunStatus
from app.schemas.action import (
    ActionExecutionRead,
    NextBestActionRead,
    PolicyDecision,
)
from app.schemas.evidence import EvidenceRead
from app.schemas.risk import PatternResult, RiskSignals


class Finding(BaseModel):
    """A provernanced conclusion produced by the investigation."""

    claim: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    confidence: float | None = None


class BelievedPattern(BaseModel):
    pattern: str
    rationale: str = ""
    evidence_ids: list[str] = Field(default_factory=list)


class SimilarCase(BaseModel):
    case_id: str
    pattern: str | None = None
    similarity_score: float | None = None
    verdict: str | None = None
    exposure_usd: float | None = None
    txn_count: int | None = None
    reason: str = ""


class GraphNode(BaseModel):
    id: str
    type: str
    label: str = ""
    attrs: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    attrs: dict[str, Any] = Field(default_factory=dict)


class InvestigationResult(BaseModel):
    # Prompt §28: "evidence-first results should contain findings, evidence IDs
    # (not embedding evidence payloads), the path followed, validation results,
    # contradictions, and any missing evidence still needed."
    case_id: str
    findings: list[Finding] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    path: list[str] = Field(default_factory=list)
    validation: str = ""
    contradictions: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)

    risk: RiskSignals | None = None
    patterns: list[PatternResult] = Field(default_factory=list)
    believed_pattern: BelievedPattern | None = None

    next_best_actions: list[NextBestActionRead] = Field(default_factory=list)
    policy_decision: PolicyDecision | None = None
    action_execution: ActionExecutionRead | None = None
    explanation: str = ""

    timeline: list[dict[str, Any]] = Field(default_factory=list)
    similar_cases: list[SimilarCase] = Field(default_factory=list)
    evidence_refs: list[EvidenceRead] = Field(default_factory=list)
    completed_at: datetime | None = None
    run_status: RunStatus | None = None