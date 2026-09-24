from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ActionState, ActionType, ApprovalRoute


class ActionRecommendation(BaseModel):
    """The agent's proposed next-best action before policy evaluation."""

    phase: str
    action: ActionType
    route: ApprovalRoute | None = None
    reason: str = ""
    policy_rule: str = ""


class PolicyDecision(BaseModel):
    """Deterministic policy-engine verdict on a proposed action."""

    request_id: str = ""
    action: ActionType
    state: ActionState
    approval_required: bool = False
    approval_route: ApprovalRoute | None = None
    matched_rules: list[str] = Field(default_factory=list)
    policy_version: str = "1.0.0"
    decision_detail: str = ""


class ApprovalRequest(BaseModel):
    """Staff decision on an action awaiting approval."""

    approval_id: str | None = None
    action_type: ActionType | None = None
    decision: str  # APPROVED | DENIED
    decided_by: str = "analyst"
    notes: str = ""


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    approval_id: str
    case_id: str
    route: ApprovalRoute
    decided_by: str | None = None
    decision: str | None = None
    decided_at: datetime | None = None
    notes: str = ""


class ActionExecutionCreate(BaseModel):
    """Submit an action for policy check and execution."""

    action: ActionType
    idempotency_key: str
    reason: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class ActionExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: str
    action: ActionType
    state: ActionState
    route: ApprovalRoute | None = None
    approval_required: bool = False
    result_payload: dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime | None = None
    policy_decision: PolicyDecision | None = None


class NextBestActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: str
    phase: str
    action: ActionType
    route: ApprovalRoute
    reason: str = ""
    policy_rule: str = ""
    order_index: int = 0


class SARSubject(BaseModel):
    role: str = "Principal"
    identifier: str = ""


class SARContent(BaseModel):
    reason: str
    narrative: str = ""
    subjects: list[SARSubject] = Field(default_factory=list)
    total_amount_usd: float = 0.0
    activity_dates: list[str] = Field(default_factory=list)