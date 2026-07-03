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

Runs standalone — its own repo, own `docker-compose.yml`, own `deploy.sh`.
It is **not** part of the homeserver orchestrator's build/sync/deploy graph.

For HTTPS, the container joins the existing `homeserver_default` Docker
network (via `docker-compose.prod.yml`, external network) so the shared
Caddy instance (already holding ports 80/443) can reverse-proxy to it by
container name — see the `a2a.{$CADDY_HOST}` block in `../CNCSearch/Caddyfile`.
A real TLS cert isn't possible any other way here: sslip.io has no DNS-01
API, and this container can't bind 80/443 itself (the homeserver Caddy
already does).

Public URL: `https://a2a.<server-ip-with-dashes>.sslip.io`

Requires `CADDY_HOST` in this project's own `.env` on the server, matching
the value already set in `../homeserver/.env`.

```bash
bash deploy.sh
```

`deploy.sh` syncs this repo and runs
`docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`.
Local dev (`docker compose up -d --build` with no explicit `-f` flags) instead
picks up `docker-compose.override.yml`, which publishes port 8000 on
`127.0.0.1` for local testing — no Caddy or `CADDY_HOST` needed.

**One manual step after the first deploy:** the shared Caddyfile is a
bind-mounted single file. A running Caddy container won't notice the new
`a2a.{$CADDY_HOST}` entry until it's force-recreated:
`ssh hetzner "cd /home/garminbot/homeserver && docker compose up -d --force-recreate caddy"`.

## OutSystems ODC integration

ODC acts as an A2A client: it should resolve the Agent Card at
`/.well-known/agent-card.json`, then POST a JSON-RPC `SendMessage` (or
`message/send`) request to `/` with the name to greet in the message's text
part.

**Not yet verified against real ODC.** This has only been tested with curl.
ODC's actual A2A client behavior (exact request shape, auth expectations,
which method name/version it sends) is unconfirmed — test directly against
ODC before treating this as proven.
