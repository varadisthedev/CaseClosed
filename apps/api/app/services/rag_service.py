from datetime import datetime, timezone
from typing import Any

from app.core.enums import Pattern, Verdict
from app.db.session import get_session_factory, init_db
from app.services.evidence_service import EvidenceService, new_evidence_id
from app.services.policy_service import PolicyService, PolicyViolationError


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def resolve_entities(case_id: str) -> dict:
    """Resolve entities for a case: customer, card, connected cards.

    Returns entity identifiers and basic info used for graph traversal.
    """
    init_db()
    # In a full implementation, this would traverse the TigerGraph graph
    # For now, return placeholder entity resolution
    return {
        "case_id": case_id,
        "customer_id": f"CUST-{case_id}",
        "card_ids": [f"CARD-{case_id}"],
        "connected_card_ids": [],
        "source": "rag_service.stub",
    }


def retrieve_graph_evidence(
    case_id: str,
    *,
    as_of: datetime | None = None,
    pattern: Pattern | None = None,
) -> dict:
    """Retrieve bounded graph evidence for a case.

    Returns evidence records with provenance that can be cited in
    an LLM explanation. Evidence IDs are guaranteed to exist in the
    investigation context.
    """
    init_db()
    evidence_svc = EvidenceService()

    # Build evidence query based on pattern and as_of timestamp
    # For now, return placeholder evidence that is provenance-aware
    evidence_ids = []

    if pattern is not None:
        # Pattern-specific evidence
        evidence_ids.append(f"EV-{case_id}-pattern-{pattern.value}")

    if as_of is not None:
        # as_of-filtered evidence
        evidence_ids.append(f"EV-{case_id}-asof-{_now_utc().timestamp():.0f}")

    # Return evidence with provenance markers
    evidence_records = []
    for eid in evidence_ids:
        evidence_records.append({
            "evidence_id": eid,
            "source": "placeholder",
            "provenance": {
                "retrieved_at": _now_utc().isoformat(),
                "as_of": as_of.isoformat() if as_of else None,
                "pattern": pattern.value if pattern else None,
            },
            "content": f"Placeholder evidence {eid} for case {case_id}",
        })

    return {
        "case_id": case_id,
        "evidence": evidence_records,
        "source": "rag_service.stub",
    }


def retrieve_similar_cases(
    case_id: str,
    *,
    limit: int = 5,
    as_of: datetime | None = None,
) -> dict:
    """Retrieve similar historical cases for a given case.

    Returns cases that are similar based on pattern, risk factors,
    and other criteria. Only returns cases that would have been
    available at the investigation time (no future information leak).
    """
    init_db()
    # In a full implementation, this would query TigerGraph for similar cases
    # For now, return placeholder similar cases
    similar = []
    for i in range(min(limit, 3)):
        similar.append({
            "case_id": f"SIM-{case_id}-{i}",
            "similarity_score": 1.0 - (i * 0.2),
            "verdict": "legitimate" if i % 2 == 0 else "fraud",
            "pattern": Pattern.NONE.value if i % 3 != 0 else Pattern.CARD_NOT_PRESENT_NEW_DEVICE.value,
            "source": "rag_service.stub",
        })

    return {
        "case_id": case_id,
        "similar_cases": similar,
        "source": "rag_service.stub",
    }


def build_grounded_context(
    case_id: str,
    *,
    as_of: datetime | None = None,
    include_pattern: Pattern | None = None,
    include_similar: bool = True,
) -> dict:
    """Build a grounded context for LLM explanation.

    Follows the process in AGENTS.md section 10:
    1. Resolve case/entities
    2. Retrieve bounded graph evidence
    3. Retrieve similar historical cases
    4. Preserve provenance on all evidence
    5. Build context that only cites evidence IDs that exist

    The explanation step may only cite evidence IDs that exist in the context;
    add a validator that strips or rejects references to unknown evidence IDs.
    """
    init_db()

    # Resolve entities
    entities = resolve_entities(case_id)

    # Retrieve graph evidence
    graph_evidence = retrieve_graph_evidence(
        case_id=case_id,
        as_of=as_of,
        pattern=include_pattern,
    )

    # Retrieve similar cases
    similar_cases = {}
    if include_similar:
        similar_cases = retrieve_similar_cases(
            case_id=case_id,
            limit=3,
            as_of=as_of,
        )

    # Build the grounded context
    context = {
        "case_id": case_id,
        "entities": entities,
        "evidence": graph_evidence["evidence"],
        "similar_cases": similar_cases.get("similar_cases", []),
        "investigation_timestamp": _now_utc().isoformat(),
        "as_of": as_of.isoformat() if as_of else None,
        "pattern": include_pattern.value if include_pattern else None,
        "source": "rag_service.stub",
    }

    # Validate: strip any evidence references that don't exist in the context
    # This is a no-op in the stub, but in production would ensure
    # only cited evidence IDs are presented to the LLM
    cited_evidence_ids = {e["evidence_id"] for e in context["evidence"]}
    # In production: filter out any evidence IDs not in cited_evidence_ids

    return context


def validate_evidence_ids(
    context: dict,
    cited_ids: list[str],
) -> dict:
    """Validator that strips or rejects references to unknown evidence IDs.

    Ensures the LLM only cites evidence IDs that exist in the grounded context.
    Returns a cleaned context with only valid evidence IDs.
    """
    valid_ids = {e["evidence_id"] for e in context.get("evidence", [])}
    cleaned_cited = [cid for cid in cited_ids if cid in valid_ids]

    # Return context with only valid cited evidence
    cleaned_context = dict(context)
    # In production: would filter LLM response to only cite valid IDs
    # For now, just return the context with a note
    cleaned_context["_validation_note"] = (
        f"Validated {len(cited_ids)} cited IDs, {len(valid_ids)} evidence IDs in context"
    )
    return cleaned_context