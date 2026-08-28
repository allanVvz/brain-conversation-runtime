from __future__ import annotations

from services import transport_client


class _Response:
    status_code = 200

    def json(self):
        return {"buffer_id": "buffer-1"}


class _Client:
    def __init__(self, calls, **kwargs):
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _Response()


def test_runtime_uses_authenticated_transport_boundary(monkeypatch):
    calls = []
    monkeypatch.setenv("BRAIN_TRANSPORT_URL", "https://transport.internal")
    monkeypatch.setenv("AI_BRAIN_WEBHOOK_TOKEN", "internal-token")
    monkeypatch.setattr(
        transport_client.httpx,
        "Client",
        lambda **kwargs: _Client(calls, **kwargs),
    )

    result = transport_client.prepare_outbound(lead={"id": 42}, text="ok")

    assert result == {"buffer_id": "buffer-1"}
    assert calls[0][0].endswith("/internal/v1/transport/messages/prepare-outbound")
    assert calls[0][1]["headers"] == {"X-Webhook-Token": "internal-token"}
