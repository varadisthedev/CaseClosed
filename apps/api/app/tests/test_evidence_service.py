from datetime import datetime, timedelta, timezone

import pytest

from app.core.enums import EvidenceRequestType
from app.core.errors import NotFoundError
from app.db.session import get_session_factory, init_db
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseCreate
from app.services.evidence_service import EvidenceService
from app.services.as_of import AsOfError, filter_after, guard_record

T0 = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _seed_case(case_id: str = "HHG-E1") -> None:
    init_db()
    db = get_session_factory()()
    repo = CaseRepository(db)
    if repo.get(case_id) is None:
        repo.create(
            CaseCreate(
                case_id=case_id,
                trigger_type="customer_report",
                trigger_text="seed",
                flagged_txn_id="T-E1",
                card_id="C1",
                customer_id="CU1",
            )
        )
        db.commit()
    db.close()


# --- shared as_of helpers ----------------------------------------------------

def test_guard_record_rejects_future() -> None:
    with pytest.raises(AsOfError):
        guard_record(T0 + timedelta(days=1), T0, label="txn")


def test_guard_record_allows_past_and_missing() -> None:
    guard_record(T0, T0)
    guard_record(T0 - timedelta(days=1), T0)
    guard_record(None, T0)
    guard_record(T0 + timedelta(days=1), None)


def test_filter_after_drops_future_records() -> None:
    records = [
        {"id": "a", "observed_at": T0.isoformat()},
        {"id": "b", "observed_at": (T0 + timedelta(hours=5)).isoformat()},
        {"id": "c", "observed_at": (T0 - timedelta(hours=5)).isoformat()},
    ]
    kept = filter_after(records, as_of=T0)
    assert [r["id"] for r in kept] == ["a", "c"]


# --- evidence service --------------------------------------------------------

class TestEvidenceService:
    @pytest.fixture(autouse=True)
    def _service(self):
        self.case_id = "HHG-E1"
        _seed_case(self.case_id)
        self.svc = EvidenceService()
        yield
        db = get_session_factory()()
        db.commit()
        db.close()

    def test_add_and_list_evidence(self) -> None:
        ev = self.svc.add_evidence(
            case_id=self.case_id,
            claim="txn T-E1 shares device DEV-1 with CU2",
            type="graph",
            source="placeholder",
            source_ref="query:shared_device_investigation",
            confidence=0.9,
            as_of=T0,
        )
        assert ev.evidence_id.startswith("EV-")
        assert ev.source == "placeholder"
        assert ev.provisional is True
        assert ev.as_of == T0

    def test_evidence_id_validation(self) -> None:
        seen = {e.evidence_id for e in self.svc.list_evidence(self.case_id)}
        assert "EV-NOPE" not in seen
        with pytest.raises(NotFoundError):
            self.svc.assert_known(self.case_id, ["EV-NOPE"])

    def test_final_context_rejects_future_evidence(self) -> None:
        from app.services.as_of import AsOfError

        # future evidence makes the whole final context unsafe: refuse it.
        self.svc.add_evidence(
            case_id=self.case_id,
            claim="observed after cut-off",
            source="placeholder",
            as_of=T0 + timedelta(days=10),
        )
        with pytest.raises(AsOfError):
            self.svc.final_context(self.case_id, as_of=T0)

        # a case with only past + at-cut-off evidence builds a clean context
        other = "HHG-CAO"
        _seed_case(other)
        self.svc.add_evidence(
            case_id=other,
            claim="observed on cut-off",
            source="placeholder",
            as_of=T0,
        )
        blocks = self.svc.final_context(other, as_of=T0)
        claims = [b["claim"] for b in blocks]
        assert "observed on cut-off" in claims
        assert "observed after cut-off" not in claims