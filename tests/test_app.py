import os
os.environ["AI_ENABLED"] = "false"  # offline mode for deterministic tests

from app import app


def test_health():
    c = app.test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"
    assert r.get_json()["ai_enabled"] is False


def test_chat_offline():
    c = app.test_client()
    r = c.post("/chat", json={"message": "what are your hours"})
    assert r.status_code == 200
    assert "hours" in r.get_json()["reply"].lower()


def test_classify_offline():
    c = app.test_client()
    r = c.post("/chat/multi", json={"messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 200


def test_missing_message():
    c = app.test_client()
    r = c.post("/chat", json={})
    assert r.status_code == 400
