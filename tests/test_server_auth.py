"""Internal-token middleware tests for task_builder.server.

The middleware is opt-in via INTERNAL_PROXY_TOKEN env var:

* Unset (local dev) → middleware is a no-op; existing tests pass unchanged.
* Set → every /api/* request must carry a matching X-Internal-Token header.

Public paths (/, /static/*, /api/health) bypass the check unconditionally so
container liveness probes and the legacy static UI work regardless.
"""
from __future__ import annotations

import importlib
from unittest.mock import patch

from fastapi.testclient import TestClient


def _reload_server(monkeypatch, token: str | None):
    if token is None:
        monkeypatch.delenv("INTERNAL_PROXY_TOKEN", raising=False)
    else:
        monkeypatch.setenv("INTERNAL_PROXY_TOKEN", token)
    import task_builder.server as srv
    return importlib.reload(srv)


def test_health_bypasses_token_check_when_token_set(monkeypatch):
    srv = _reload_server(monkeypatch, "shh-secret")
    client = TestClient(srv.app)
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_chat_rejects_request_without_token_when_token_set(monkeypatch):
    srv = _reload_server(monkeypatch, "shh-secret")
    client = TestClient(srv.app)
    resp = client.post("/api/chat", json={"session_id": "x", "message": "hi"})
    assert resp.status_code == 403
    assert "X-Internal-Token" in resp.json()["detail"]


def test_chat_accepts_request_with_matching_token(monkeypatch):
    srv = _reload_server(monkeypatch, "shh-secret")
    # Mock the DB layer so we only exercise the middleware → handler path.
    with patch.object(srv, "load_session", return_value=None):
        client = TestClient(srv.app)
        resp = client.post(
            "/api/chat",
            json={"session_id": "x", "message": "hi"},
            headers={"X-Internal-Token": "shh-secret"},
        )
    # Past the middleware (no 403) → handler returns 404 because the mocked
    # session lookup yields None.
    assert resp.status_code == 404


def test_no_middleware_when_token_unset(monkeypatch):
    """Local dev path: no INTERNAL_PROXY_TOKEN env → middleware is a no-op."""
    srv = _reload_server(monkeypatch, None)
    with patch.object(srv, "load_session", return_value=None):
        client = TestClient(srv.app)
        resp = client.post("/api/chat", json={"session_id": "x", "message": "hi"})
    assert resp.status_code == 404  # passes middleware → handler 404


def test_session_forwards_testmaker_id_header(monkeypatch):
    """X-Testmaker-Id header propagates into create_conversation(started_by=…)."""
    srv = _reload_server(monkeypatch, None)
    with patch.object(srv, "create_conversation", return_value="conv-1") as create:
        client = TestClient(srv.app)
        resp = client.post(
            "/api/session",
            headers={"X-Testmaker-Id": "tm-uuid-42"},
        )
        assert resp.status_code == 200
        create.assert_called_once()
        kwargs = create.call_args.kwargs
        assert kwargs["started_by"] == "tm-uuid-42"


def test_session_passes_none_when_no_testmaker_header(monkeypatch):
    srv = _reload_server(monkeypatch, None)
    with patch.object(srv, "create_conversation", return_value="conv-2") as create:
        client = TestClient(srv.app)
        client.post("/api/session")
        assert create.call_args.kwargs["started_by"] is None
