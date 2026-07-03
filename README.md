# a2a

Minimal [A2A protocol](https://a2a-protocol.org/) agent — a proof-of-concept
to validate calling an A2A agent from OutSystems ODC. Receives a name and
replies `Olá <name>`.

## Stack

- Python 3.11, FastAPI, `a2a-sdk` 1.1.0 (JSON-RPC 2.0 transport)
- Supports both the current v1.0 `SendMessage` method and the legacy v0.3
  `message/send` method (compat mode enabled)

## Endpoints

- `GET /.well-known/agent-card.json` — Agent Card (capabilities, skills)
- `POST /` — JSON-RPC 2.0 endpoint (`SendMessage` / `message/send`)
- `GET /health` — health check

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate   # or source .venv/bin/activate on Linux/Mac
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Server listens on `http://localhost:8000`.

### Test with curl

v1.0 (current spec):

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -H "A2A-Version: 1.0" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "SendMessage",
    "params": {
      "message": {
        "messageId": "msg-1",
        "role": "ROLE_USER",
        "parts": [{"text": "Nelson"}]
      }
    }
  }'
```

Legacy v0.3 (no version header needed):

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "msg-1",
        "role": "user",
        "parts": [{"kind": "text", "text": "Nelson"}]
      }
    }
  }'
```

Both return a message with `"Olá Nelson"` in `parts[0].text`.

## Run with Docker (local)

```bash
docker compose up -d --build
```

## Deploy to Hetzner

Deployed via the `homeserver` orchestrator (`../homeserver/docker-compose.yml`,
service name `a2a`), reverse-proxied by Caddy at
`https://a2a.<server-ip-with-dashes>.sslip.io` (see `../CNCSearch/Caddyfile`).

```bash
bash deploy.sh
```

## OutSystems ODC integration

ODC acts as an A2A client: it should resolve the Agent Card at
`/.well-known/agent-card.json`, then POST a JSON-RPC `SendMessage` (or
`message/send`) request to `/` with the name to greet in the message's text
part.

**Not yet verified against real ODC.** This has only been tested with curl.
ODC's actual A2A client behavior (exact request shape, auth expectations,
which method name/version it sends) is unconfirmed — test directly against
ODC before treating this as proven.
