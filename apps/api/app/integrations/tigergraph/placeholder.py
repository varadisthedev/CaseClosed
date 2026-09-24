from datetime import datetime
from typing import Any

from app.core.enums import Pattern
from app.schemas.risk import PatternResult


class PlaceholderGraphClient:
    """Synthetic graph fixture data so every graph capability is callable.

    # PLACEHOLDER(tigergraph): replaced by the TigerGraph MCP client once the
    # schema, GSQL queries and loader are available. All data returned here is
    # clearly synthetic fixture data (``source="placeholder"``) and must never
    # be presented as real evidence.
    """

    source = "placeholder"

    # Deterministic stub cards/customers/devices keyed by input entity so the
    # same input always yields the same output (deterministic where it matters).
    _NEIGHBORS = {
        "card": {"C1": ["C2", "C3"], "C2": ["C1"], "C3": ["C1"]},
        "customer": {"CU1": ["CU2"], "CU2": ["CU1"]},
        "device": {"DEV-1": ["DEV-2"], "DEV-2": ["DEV-1"]},
    }

    def transaction_context(self, txn_id: str, as_of: datetime) -> dict[str, Any]:
        return {
            "source": self.source,
            "transaction_id": txn_id,
            "card_id": "C-FIXTURE",
            "customer_id": "CU-FIXTURE",
            "amount_usd": 249.99,
            "observed_at": as_of.isoformat(),
            "note": "synthetic fixture",
        }

    def customer_profile(self, customer_id: str, as_of: datetime) -> dict[str, Any]:
        return {
            "source": self.source,
            "customer_id": customer_id,
            "card_ids": ["C1"],
            "device_ids": ["DEV-1"],
            "is_fixture": True,
        }

    def card_network(self, card_id: str, as_of: datetime) -> dict[str, Any]:
        neighbors = self._NEIGHBORS["card"].get(card_id, [])
        return {
            "source": self.source,
            "card_id": card_id,
            "connected_cards": neighbors,
            "customers": ["CU1", "CU2"],
            "transaction_count": 3,
            "is_fixture": True,
        }

    def shared_device_investigation(
        self, device_id: str, as_of: datetime
    ) -> dict[str, Any]:
        neighbors = self._NEIGHBORS["device"].get(device_id, [])
        return {
            "source": self.source,
            "device_id": device_id,
            "connected_devices": neighbors,
            "customers": ["CU1", "CU2"],
            "cards": ["C1", "C2"],
            "transaction_count": 2,
            "is_fixture": True,
        }

    def related_transactions(
        self, txn_id: str, as_of: datetime, limit: int = 20
    ) -> dict[str, Any]:
        return {
            "source": self.source,
            "anchor_transaction_id": txn_id,
            "related_transactions": [
                {"transaction_id": "T-REL-1", "relation": "same_card", "amount_usd": 120.0},
                {"transaction_id": "T-REL-2", "relation": "same_device", "amount_usd": 89.0},
            ][:limit],
            "is_fixture": True,
        }

    def fraud_proximity(
        self, entity_id: str, entity_type: str, as_of: datetime
    ) -> dict[str, Any]:
        return {
            "source": self.source,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "hops_to_confirmed_fraud": 1,  # fixture value
            "intermediaries": ["NODE-X"],
            "is_fixture": True,
        }

    def similar_historical_cases(
        self, case_id: str, as_of: datetime, limit: int = 10
    ) -> dict[str, Any]:
        return {
            "source": self.source,
            "case_id": case_id,
            "similar_cases": [
                {
                    "prior_case_id": f"HHG-PRIOR-{i}",
                    "similarity": 0.9 - 0.1 * i,
                    "pattern": "card_not_present_fraud",
                    "verdict": "confirmed_fraud",
                }
                for i in range(min(limit, 3))
            ],
            "is_fixture": True,
        }

    def pattern_detection(
        self, card_id: str, customer_id: str, as_of: datetime, txn_id: str | None = None
    ) -> list[PatternResult]:
        return [
            PatternResult(
                pattern=Pattern.CARD_NOT_PRESENT_FRAUD,
                matched=True,
                description="synthetic fixture: out-of-region CNP use",
                evidence_ids=[],
            )
        ]

    def graph_risk_signals(
        self, card_id: str, customer_id: str, as_of: datetime
    ) -> dict[str, Any]:
        return {
            "source": self.source,
            "graph_risk_score": 0.6,
            "signals": {
                "shared_customer_count": 2,
                "new_device_msd": 30,
                "velocity_6h": 4,
            },
            "is_fixture": True,
        }

    def case_graph_write(
        self,
        case_id: str,
        entities: dict[str, Any],
        relationships: list[dict[str, Any]],
        as_of: datetime,
    ) -> dict[str, Any]:
        return {
            "source": self.source,
            "case_id": case_id,
            "written": True,
            "graph_case_id": f"GRAPH-{case_id}",
            "entities_written": list(entities.keys()),
            "relationships_written": len(relationships),
            "is_fixture": True,
        }