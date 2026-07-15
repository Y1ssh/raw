from fastapi.testclient import TestClient

from raw.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready() -> None:
    r = client.get("/ready")
    assert r.status_code == 200
