from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import Pattern, Verdict


class RiskFactor(BaseModel):
    """One explainable driver of the risk score."""

    factor: str
    value: float | str | None = None
    contribution: float | None = None
    direction: str = "up"


class RiskAssessment(BaseModel):
    """ML risk signal for a flagged transaction.

    ``calibrated`` is false unless probabilities have actually been
    demonstrated (AGENTS.md section 9). Models output a score/band.
    """

    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    score: float
    band: str = "UNKNOWN"
    top_factors: list[RiskFactor] = Field(default_factory=list)
    model_version: str = "unversioned"
    calibrated: bool = False
    calibrated_auprc: float | None = None
    source: str = "ml_model"  # or "placeholder" / "rule"
    fallback_used: bool = False
    generated_at: datetime | None = None


class PatternResult(BaseModel):
    pattern: Pattern
    matched: bool
    description: str = ""
    evidence_ids: list[str] = Field(default_factory=list)


class RiskSignals(BaseModel):
    ml: RiskAssessment | None = None
    patterns: list[PatternResult] = Field(default_factory=list)
    verdict: Verdict | None = None