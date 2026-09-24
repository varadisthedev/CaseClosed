from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["service"] == "caseclosed-api"
    assert "version" in body


def test_request_id_header(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.headers.get("X-Request-ID")


def test_request_id_echoed(client: TestClient) -> None:
    resp = client.get("/health", headers={"X-Request-ID": "abc123"})
    assert resp.headers.get("X-Request-ID") == "abc123"


def test_docs_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200