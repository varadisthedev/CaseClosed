#!/usr/bin/env bash
set -euo pipefail

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-4}"

wait_for_db() {
    if [ -z "${DATABASE_URL:-}" ]; then
        echo "[entrypoint] DATABASE_URL not set, skipping database wait"
        return 0
    fi
    echo "[entrypoint] Waiting for database..."
    python - <<'PY'
import asyncio
import os
import sys

import asyncpg

url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")


async def main() -> None:
    for attempt in range(30):
        try:
            conn = await asyncpg.connect(url, timeout=3)
            await conn.close()
            print("[entrypoint] Database is ready")
            return
        except Exception as exc:  # noqa: BLE001
            print(f"[entrypoint] DB not ready ({attempt + 1}/30): {exc}")
            await asyncio.sleep(2)
    sys.exit("[entrypoint] Database did not become ready in time")


asyncio.run(main())
PY
}

run_migrations() {
    echo "[entrypoint] Running Alembic migrations..."
    alembic -c /app/alembic.ini upgrade head
}

seed_cases() {
    echo "[entrypoint] Seeding case pack..."
    python -m scripts.seed_case_pack
}

case "${1:-serve}" in
    migrate)
        wait_for_db
        run_migrations
        ;;
    seed)
        wait_for_db
        run_migrations
        seed_cases
        ;;
    test)
        wait_for_db
        run_migrations
        exec pytest -v
        ;;
    serve)
        wait_for_db
        run_migrations
        if [ "${APP_ENV:-development}" = "production" ]; then
            echo "[entrypoint] Starting uvicorn (production, ${WEB_CONCURRENCY} workers)"
            exec uvicorn app.main:app \
                --host "$APP_HOST" --port "$APP_PORT" \
                --workers "$WEB_CONCURRENCY"
        else
            echo "[entrypoint] Starting uvicorn (development, reload)"
            exec uvicorn app.main:app \
                --host "$APP_HOST" --port "$APP_PORT" --reload
        fi
        ;;
    *)
        exec "$@"
        ;;
esac
