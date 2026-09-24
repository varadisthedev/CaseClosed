from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import EvidenceRequestStatus, EvidenceRequestType
from app.db.models import Evidence, EvidenceRequest
from app.schemas.evidence import EvidenceRequestCreate


class EvidenceRepository:
    """Persistence for evidence records and evidence requests. No business logic."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        evidence_id: str,
        case_id: str,
        claim: str,
        type: str = "graph",
        source: str = "placeholder",
        source_ref: str = "",
        confidence: float | None = None,
        entity_ids: list[str] | None = None,
        payload: dict[str, Any] | None = None,
        as_of: datetime | None = None,
        provisional: bool = True,
    ) -> Evidence:
        evidence = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            claim=claim,
            type=type,
            source=source,
            source_ref=source_ref,
            confidence=confidence,
            entity_ids=entity_ids or [],
            payload=payload or {},
            as_of=as_of,
            provisional=provisional,
        )
        self.session.add(evidence)
        return evidence

    def get(self, evidence_id: str) -> Evidence | None:
        return self.session.scalar(
            select(Evidence).where(Evidence.evidence_id == evidence_id)
        )

    def get_for_case(self, case_id: str, source: str | None = None) -> list[Evidence]:
        stmt = select(Evidence).where(Evidence.case_id == case_id)
        if source:
            stmt = stmt.where(Evidence.source == source)
        stmt = stmt.order_by(Evidence.created_at)
        return list(self.session.scalars(stmt).all())

    def get_by_ids(self, evidence_ids: list[str]) -> list[Evidence]:
        stmt = select(Evidence).where(Evidence.evidence_id.in_(evidence_ids))
        return list(self.session.scalars(stmt).all())

    def create_request(
        self,
        *,
        request_id: str,
        case_id: str,
        type: EvidenceRequestType,
        asked_after_step: int = 0,
        assumed_response: str = "",
        status: EvidenceRequestStatus = EvidenceRequestStatus.PENDING,
    ) -> EvidenceRequest:
        request = EvidenceRequest(
            request_id=request_id,
            case_id=case_id,
            type=type,
            asked_after_step=asked_after_step,
            assumed_response=assumed_response,
            status=status,
        )
        self.session.add(request)
        return request

    def list_requests(self, case_id: str) -> list[EvidenceRequest]:
        stmt = select(EvidenceRequest).where(EvidenceRequest.case_id == case_id)
        return list(self.session.scalars(stmt).all())

    def get_request(self, request_id: str) -> EvidenceRequest | None:
        return self.session.scalar(
            select(EvidenceRequest).where(EvidenceRequest.request_id == request_id)
        )

    def update_request(self, request_id: str, **values: Any) -> EvidenceRequest | None:
        request = self.get_request(request_id)
        if request is None:
            return None
        for key, value in values.items():
            if hasattr(request, key):
                setattr(request, key, value)
        return request