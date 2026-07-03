#!/usr/bin/env bash
#
# deploy.sh - Pull a2a, rebuild and restart it (standalone, own docker-compose.yml)
#
# Usage: bash deploy.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== a2a Deploy ==="

echo "[1/3] Syncing to origin/main..."
git fetch origin
git reset --hard origin/main

COMPOSE_ARGS="-f docker-compose.yml -f docker-compose.prod.yml"

echo "[2/3] Rebuilding and restarting a2a..."
docker compose $COMPOSE_ARGS up -d --build

echo "[3/3] Recent logs:"
docker compose $COMPOSE_ARGS logs --tail=30 a2a
