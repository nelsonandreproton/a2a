#!/usr/bin/env bash
#
# deploy.sh - Pull a2a, rebuild and restart the a2a service
#
# Usage: bash deploy.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/../homeserver/docker-compose.yml"

cd "$SCRIPT_DIR"

echo "=== a2a Deploy ==="

echo "[1/3] Syncing to origin/main..."
git fetch origin
git reset --hard origin/main

echo "[2/3] Rebuilding and restarting a2a..."
docker compose -f "$COMPOSE_FILE" up -d --build a2a

echo "[3/3] Recent logs:"
docker compose -f "$COMPOSE_FILE" logs --tail=30 a2a
