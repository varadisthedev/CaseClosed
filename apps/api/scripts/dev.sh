#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$API_DIR"

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

alembic -c "$API_DIR/alembic.ini" upgrade head

exec uvicorn app.main:app \
    --reload \
    --host "${APP_HOST:-0.0.0.0}" \
    --port "${APP_PORT:-8000}"
