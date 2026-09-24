from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from app.schemas.risk import PatternResult


@runtime_checkable
class GraphClient(Protocol):
    """Contract for graph-investigation capabilities (AGENTS.md section 8).

    Every method takes an ``as_of`` timestamp and MUST NOT return data
    observed after it (see AGENTS.md section 21). Real implementations
    (TigerGraph MCP) must satisfy this exact interface so the placeholder can
    be swapped purely by config.
    """

    def transaction_context(self, txn_id: str, as_of: datetime) -> dict[str, Any]: ...

    def customer_profile(self, customer_id: str, as_of: datetime) -> dict[str, Any]: ...

    def card_network(self, card_id: str, as_of: datetime) -> dict[str, Any]: ...

    def shared_device_investigation(
        self, device_id: str, as_of: datetime
    ) -> dict[str, Any]: ...

    def related_transactions(
        self, txn_id: str, as_of: datetime, limit: int = 20
    ) -> dict[str, Any]: ...

    def fraud_proximity(
        self, entity_id: str, entity_type: str, as_of: datetime
    ) -> dict[str, Any]: ...

    def similar_historical_cases(
        self, case_id: str, as_of: datetime, limit: int = 10
    ) -> dict[str, Any]: ...

    def pattern_detection(
        self, card_id: str, customer_id: str, as_of: datetime, txn_id: str | None = None
    ) -> list[PatternResult]: ...

    def graph_risk_signals(
        self, card_id: str, customer_id: str, as_of: datetime
    ) -> dict[str, Any]: ...

    def case_graph_write(
        self,
        case_id: str,
        entities: dict[str, Any],
        relationships: list[dict[str, Any]],
        as_of: datetime,
    ) -> dict[str, Any]: ...