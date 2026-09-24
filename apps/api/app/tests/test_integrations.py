from datetime import datetime, timezone

import pytest

from app.core.config import Settings
from app.ml.model import RiskModel
from app.ml.predictor import RiskPredictor


def test_graph_placeholder_is_deterministic_and_flagged() -> None:
    from app.integrations.tigergraph.placeholder import PlaceholderGraphClient

    client = PlaceholderGraphClient()
    as_of = datetime(2024, 1, 1, tzinfo=timezone.utc)
    a = client.transaction_context("T1", as_of)
    b = client.transaction_context("T1", as_of)
    assert a == b  # deterministic fixture data
    assert a["source"] == "placeholder"


def test_graph_capabilities_are_callable() -> None:
    from app.integrations.tigergraph.placeholder import PlaceholderGraphClient

    client = PlaceholderGraphClient()
    as_of = datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert client.card_network("C1", as_of)["connected_cards"] == ["C2", "C3"]
    assert client.customer_profile("CU1", as_of)["card_ids"] == ["C1"]
    assert client.case_graph_write("HHG-1", {"customer": "CU1"}, [], as_of)["written"]
    patterns = client.pattern_detection("C1", "CU1", as_of)
    assert patterns[0].pattern.value == "card_not_present_fraud"


def test_mcp_graph_client_skeleton_raises() -> None:
    from app.integrations.mcp.graph_client import McpGraphClient

    client = McpGraphClient()
    with pytest.raises(NotImplementedError, match="PLACEHOLDER"):
        client.customer_profile("CU1", datetime.now(timezone.utc))


def test_graph_factory_selects_mcp_by_config() -> None:
    from app.integrations.tigergraph.factory import get_graph_client

    placeholders = get_graph_client(Settings(GRAPH_BACKEND="placeholder"))
    assert isinstance(placeholders, object)
    mcp = get_graph_client(Settings(GRAPH_BACKEND="mcp"))
    assert mcp.__class__.__name__ == "McpGraphClient"


def test_placeholder_llm_only_cites_given_evidence() -> None:
    from app.integrations.llm.placeholder import PlaceholderLLMClient

    client = PlaceholderLLMClient()
    assert client.source == "placeholder"
    out = client.generate(
        [
            {"role": "user", "content": "EV-100 and EV-101 are relevant."},
            {"role": "assistant", "content": "EV-100, EV-101"},
        ]
    )
    assert "EV-100" in out and "EV-101" in out
    assert "EV-999" not in out  # no invented evidence

    empty = client.generate([{"role": "user", "content": "no ids here"}])
    assert "EV-" not in empty  # no evidence -> no cited IDs


def test_placeholder_llm_json_schema() -> None:
    from app.integrations.llm.placeholder import PlaceholderLLMClient

    client = PlaceholderLLMClient()
    out = client.generate(
        [{"role": "user", "content": "EV-1"}], response_schema={"type": "object"}
    )
    import json

    parsed = json.loads(out)
    assert parsed["evidence_ids"] == ["EV-1"]


def test_in_memory_vector_store_keyword_and_as_of() -> None:
    from app.integrations.vector_store.in_memory import InMemoryVectorStore

    store = InMemoryVectorStore()
    t1 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2024, 2, 1, tzinfo=timezone.utc)
    store.upsert(
        "doc-old",
        {"text": "card testing policy blocks card"},
        as_of=t1,
    )
    store.upsert(
        "doc-new",
        {"text": "account takeover step-up auth"},
        as_of=t2,
    )
    hits = store.search("card testing", top_k=5, as_of=datetime(2024, 1, 31, tzinfo=timezone.utc))
    # doc-new is after as_of and must be excluded
    assert "doc-old" in [h["doc_id"] for h in hits]
    assert "doc-new" not in [h["doc_id"] for h in hits]


def test_ml_stub_fallback_is_deterministic() -> None:
    model = RiskModel(model_path="app/ml/artifacts/does-not-exist.joblib")
    assert model.loaded is False
    a = model.predict({"transaction_id": "T123"})
    b = model.predict({"transaction_id": "T123"})
    assert a["score"] == b["score"]
    assert a["calibrated"] is False
    assert a["fallback_used"] is True


def test_risk_predictor_wraps_stub() -> None:
    predictor = RiskPredictor(model=RiskModel(model_path="app/ml/artifacts/nope.joblib"))
    assessment = predictor.assess(transaction_id="TX12", features={"amount": 100.0})
    assert assessment.source == "placeholder"
    assert 0.0 <= assessment.score <= 1.0
    assert assessment.band in {"LOW", "MEDIUM", "HIGH"}
    assert assessment.calibrated is False