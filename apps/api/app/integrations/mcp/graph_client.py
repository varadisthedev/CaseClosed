from datetime import datetime
from typing import Any

from app.schemas.risk import PatternResult


class McpGraphClient:
    """Skeleton for the TigerGraph MCP-backed graph client.

    # PLACEHOLDER(tigergraph-mcp): wire this to the TigerGraph MCP server once
    # the MCP integration exists. It must satisfy the same interface as
    # PlaceholderGraphClient (see app/integrations/tigergraph/graph_client.py).
    """

    source = "tigergraph"

    def _raise(self, method: str) -> None:
        raise NotImplementedError(
            f"PLACEHOLDER(tigergraph-mcp): TigerGraph MCP not wired yet ({method})"
        )

    def transaction_context(self, txn_id: str, as_of: datetime) -> dict[str, Any]:
        self._raise("transaction_context")

    def customer_profile(self, customer_id: str, as_of: datetime) -> dict[str, Any]:
        self._raise("customer_profile")

    def card_network(self, card_id: str, as_of: datetime) -> dict[str, Any]:
        self._raise("card_network")

    def shared_device_investigation(
        self, device_id: str, as_of: datetime
    ) -> dict[str, Any]:
        self._raise("shared_device_investigation")

    def related_transactions(
        self, txn_id: str, as_of: datetime, limit: int = 20
    ) -> dict[str, Any]:
        self._raise("related_transactions")

    def fraud_proximity(
        self, entity_id: str, entity_type: str, as_of: datetime
    ) -> dict[str, Any]:
        self._raise("fraud_proximity")

    def similar_historical_cases(
        self, case_id: str, as_of: datetime, limit: int = 10
    ) -> dict[str, Any]:
        self._raise("similar_historical_cases")

    def pattern_detection(
        self, card_id: str, customer_id: str, as_of: datetime, txn_id: str | None = None
    ) -> list[PatternResult]:
        self._raise("pattern_detection")

    def graph_risk_signals(
        self, card_id: str, customer_id: str, as_of: datetime
    ) -> dict[str, Any]:
        self._raise("graph_risk_signals")

    def case_graph_write(
        self,
        case_id: str,
        entities: dict[str, Any],
        relationships: list[dict[str, Any]],
        as_of: datetime,
    ) -> dict[str, Any]:
        self._raise("case_graph_write")