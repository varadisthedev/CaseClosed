from datetime import datetime
from typing import Any

from app.core.errors import NotFoundError
from app.core.enums import EvidenceRequestType
from app.db.session import get_session_factory
from app.repositories.action_repository import ActionRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence import EvidenceRead, EvidenceRequestRead
from app.services.as_of import guard_record


class EvidenceService:
    """Coordinates evidence capture and provenance rules (AGENTS.md section 20).

    Every conclusion should be traceable to evidence records carrying a stable
    ID, type, source, ``source_ref``, ``created_at``, ``as_of``, ``confidence``
    and a payload.
    """

    def __init__(self, session=None) -> None:
        self.session = session or get_session_factory()()
        self.repo = EvidenceRepository(self.session)
        self.cases = CaseRepository(self.session)
        self.audit = ActionRepository(self.session)

    def _require_case(self, case_id: str) -> None:
        if self.cases.get(case_id) is None:
            raise NotFoundError(f"Unknown case: {case_id}")

    def add_evidence(
        self,
        *,
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
        evidence_id: str | None = None,
    ) -> EvidenceRead:
        self._require_case(case_id)
        ev_id = evidence_id or new_evidence_id(case_id)
        record = self.repo.create(
            evidence_id=ev_id,
            case_id=case_id,
            claim=claim,
            type=type,
            source=source,
            source_ref=source_ref,
            confidence=confidence,
            entity_ids=entity_ids,
            payload=payload,
            as_of=as_of,
            provisional=provisional,
        )
        self.session.commit()
        return EvidenceRead.model_validate(record)

    # --- evidence requests (investigation control flow) ---------------------

    def request_evidence(
        self,
        *,
        case_id: str,
        type: EvidenceRequestType,
        asked_after_step: int = 0,
        assumed_response: str = "",
    ) -> EvidenceRequestRead:
        """Persist a request for missing evidence. Returns request record."""
        self._require_case(case_id)
        import uuid

        request = self.repo.create_request(
            request_id=new_request_id(case_id),
            case_id=case_id,
            type=type,
            asked_after_step=asked_after_step,
            assumed_response=assumed_response,
        )
        self.audit.log_audit(
            event_id=new_event_id(),
            event_type="evidence.requested",
            case_id=case_id,
            actor="agent",
            detail={"type": type.value, "after_step": asked_after_step},
        )
        self.session.commit()
        return EvidenceRequestRead.model_validate(request)

    def list_evidence(self, case_id: str, source: str | None = None) -> list[EvidenceRead]:
        self._require_case(case_id)
        records = self.repo.get_for_case(case_id, source=source)
        return [EvidenceRead.model_validate(r) for r in records]

    def list_requests(self, case_id: str) -> list[EvidenceRequestRead]:
        self._require_case(case_id)
        requests = self.repo.list_requests(case_id)
        return [EvidenceRequestRead.model_validate(r) for r in requests]

    # --- provenance validation ----------------------------------------------

    def assert_known(self, case_id: str, evidence_ids: list[str]) -> None:
        """Reject references to evidence IDs that do not exist for this case.

        The LLM must never cite unknown evidence (grounding validator).
        """
        self._require_case(case_id)
        known = {r.evidence_id for r in self.repo.get_for_case(case_id)}
        missing = [eid for eid in evidence_ids if eid not in known]
        if missing:
            raise NotFoundError(
                f"References unknown evidence IDs: {sorted(missing)}"
            )

    def final_context(self, case_id: str, as_of: datetime | None = None) -> list[dict[str, Any]]:
        """Text context of grounded evidence for the LLM, respecting ``as_of``."""
        self._require_case(case_id)
        records = self.repo.get_for_case(case_id)
        blocks: list[dict[str, Any]] = []
        for record in records:
            guard_record(record.as_of, as_of, label=f"evidence {record.evidence_id}")
            blocks.append(
                {
                    "evidence_id": record.evidence_id,
                    "type": record.type,
                    "claim": record.claim,
                    "source": record.source,
                    "source_ref": record.source_ref,
                    "confidence": record.confidence,
                    "payload": record.payload or {},
                }
            )
        return blocks


# --- small builders ----------------------------------------------------------

def new_evidence_id(case_id: str) -> str:
    import uuid

    return f"EV-{case_id}-{uuid.uuid4().hex[:8]}"


def new_request_id(case_id: str) -> str:
    import uuid

    return f"RQ-{case_id}-{uuid.uuid4().hex[:8]}"


def new_event_id() -> str:
    import uuid

    return f"AU-{uuid.uuid4().hex[:12]}"


def current_as_of() -> datetime:
    from datetime import timezone

    return datetime.now(timezone.utc)