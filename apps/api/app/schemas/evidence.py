from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import EvidenceRequestType


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evidence_id: str
    case_id: str
    type: str = "graph"
    claim: str
    source: str = "placeholder"
    source_ref: str = ""
    confidence: float | None = None
    entity_ids: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    as_of: datetime | None = None
    provisional: bool = True
    created_at: datetime | None = None


class EvidenceRequestCreate(BaseModel):
    type: EvidenceRequestType
    asked_after_step: int = 0
    assumed_response: str = ""


class EvidenceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: str
    case_id: str
    type: EvidenceRequestType
    asked_after_step: int = 0
    assumed_response: str = ""
    status: str
    created_at: datetime | None = None