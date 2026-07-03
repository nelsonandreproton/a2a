"""Integration tests for the A2A greeter agent's HTTP surface (asserts UTF-8 accented output)."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_agent_card_is_served():
    response = client.get("/.well-known/agent-card.json")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Greeter Agent"
    assert body["skills"][0]["id"] == "greet"


def test_send_message_v1_returns_greeting():
    response = client.post(
        "/",
        headers={"A2A-Version": "1.0"},
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": "msg-1",
                    "role": "ROLE_USER",
                    "parts": [{"text": "Nelson"}],
                }
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["message"]["parts"][0]["text"] == "Olá Nelson"


def test_send_message_legacy_v0_3_returns_greeting():
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": "msg-1",
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Ana"}],
                }
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["parts"][0]["text"] == "Olá Ana"


def test_send_message_with_blank_name_defaults_to_mundo():
    response = client.post(
        "/",
        headers={"A2A-Version": "1.0"},
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": "msg-1",
                    "role": "ROLE_USER",
                    "parts": [{"text": "   "}],
                }
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["message"]["parts"][0]["text"] == "Olá mundo"
