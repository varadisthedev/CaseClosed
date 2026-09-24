from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Case,
    CaseConnectedCard,
    CaseConnectedDevice,
    CaseSimilarCase,
    CaseTransaction,
    ClosedCase,
)
from app.schemas.case import CaseCreate


class CaseRepository:
    """Persistence for cases and their relationship records. No business logic."""

    model = Case

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: CaseCreate) -> Case:
        case = Case(
            case_id=data.case_id,
            trigger_type=data.trigger_type,
            trigger_text=data.trigger_text,
            flagged_txn_id=data.flagged_txn_id,
            card_id=data.card_id,
            customer_id=data.customer_id,
            input_risk_score=data.input_risk_score,
            opened_at=data.opened_at or datetime.now(timezone.utc),
            as_of=data.as_of,
            status=None,
        )
        self.session.add(case)
        return case

    def get(self, case_id: str) -> Case | None:
        stmt = select(Case).where(Case.case_id == case_id)
        return self.session.scalar(stmt)

    def update(self, case_id: str, **values: Any) -> Case | None:
        case = self.get(case_id)
        if case is None:
            return None
        for key, value in values.items():
            if hasattr(case, key):
                setattr(case, key, value)
        return case

    def list(self, limit: int = 100, offset: int = 0) -> Sequence[Case]:
        stmt = (
            select(Case)
            .order_by(Case.opened_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()

    def add_transaction(
        self, case_id: str, transaction_id: str, *, is_flagged: bool = False,
        amount_usd: float | None = None,
    ) -> CaseTransaction:
        link = CaseTransaction(
            case_id=case_id,
            transaction_id=transaction_id,
            is_flagged=is_flagged,
            amount_usd=amount_usd,
        )
        self.session.add(link)
        return link

    def add_connected_card(self, case_id: str, card_id: str, reason: str = "") -> CaseConnectedCard:
        link = CaseConnectedCard(case_id=case_id, card_id=card_id, reason=reason)
        self.session.add(link)
        return link

    def add_connected_device(self, case_id: str, device_profile: str, reason: str = "") -> CaseConnectedDevice:
        link = CaseConnectedDevice(case_id=case_id, device_profile=device_profile, reason=reason)
        self.session.add(link)
        return link

    def add_similar_case(
        self, case_id: str, prior_case_id: str, *, similarity: float | None = None,
        rank: int | None = None, rationale: str = "",
    ) -> CaseSimilarCase:
        link = CaseSimilarCase(
            case_id=case_id,
            prior_case_id=prior_case_id,
            similarity=similarity,
            rank=rank,
            rationale=rationale,
        )
        self.session.add(link)
        return link

    def transactions(self, case_id: str) -> Sequence[CaseTransaction]:
        return self.session.scalars(
            select(CaseTransaction).where(CaseTransaction.case_id == case_id)
        ).all()

    def connected_cards(self, case_id: str) -> Sequence[CaseConnectedCard]:
        return self.session.scalars(
            select(CaseConnectedCard).where(CaseConnectedCard.case_id == case_id)
        ).all()

    def connected_devices(self, case_id: str) -> Sequence[CaseConnectedDevice]:
        return self.session.scalars(
            select(CaseConnectedDevice).where(CaseConnectedDevice.case_id == case_id)
        ).all()

    def similar_cases(self, case_id: str) -> Sequence[CaseSimilarCase]:
        return self.session.scalars(
            select(CaseSimilarCase).where(CaseSimilarCase.case_id == case_id)
        ).all()

    def save_closed_case(self, **values: Any) -> ClosedCase:
        case = ClosedCase(**values)
        self.session.add(case)
        return case

    def get_closed_case(self, case_id: str) -> ClosedCase | None:
        return self.session.scalar(
            select(ClosedCase).where(ClosedCase.case_id == case_id)
        )

    def list_closed_cases(
        self, customer_id: str | None = None, pattern: str | None = None,
        limit: int = 50,
    ) -> Sequence[ClosedCase]:
        stmt = select(ClosedCase)
        if customer_id:
            stmt = stmt.where(ClosedCase.customer_id == customer_id)
        if pattern:
            stmt = stmt.where(ClosedCase.pattern == pattern)
        return self.session.scalars(stmt.limit(limit)).all()

    def flush(self) -> None:
        self.session.flush()